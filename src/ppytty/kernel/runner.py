# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import contextlib
import heapq
import logging
import os
import select
import sys
import time

from . state import tasks, state
from . terminal import Terminal



class _PlayerStop(Exception):

    pass



_log = logging.getLogger('runner')

_STDIN_FD = sys.stdin.fileno()
_RD_FDS = [_STDIN_FD]
_NO_FDS = []

_this_module = sys.modules[__name__]



def run(task, post_prompt='[COMPLETED]'):

    # TODO: default to disable logging so as not to require callers to
    #       do that themselves if they don't care; this avoids spurious
    #       sys.stderr output resulting from messages >= warning from the
    #       default standard library's logging module.

    with Terminal() as terminal:
        state.terminal = terminal
        try:
            _run(task)
            while post_prompt:
                _ = _read_keyboard(prompt=post_prompt)
        except _PlayerStop:
            pass



def _run(top_task):

    tasks.top_task = top_task
    tasks.running.append(top_task)

    while (tasks.running or tasks.waiting_on_child or tasks.waiting_on_key or
           tasks.waiting_on_time or tasks.terminated):
        state.now = time.time()
        if not tasks.running:
            _process_tasks_waiting_on_key()
            _process_tasks_waiting_on_time()
            continue
        task = tasks.running.popleft()
        try:
            request = _run_task_until_request(task)
        except StopIteration as return_:
            _log.info('%r completed with %r', task, return_.value)
            if task is top_task:
                continue
            _process_task_completion(task, return_.value)
        else:
            _process_task_request(task, request)



def _process_task_request(task, request):

    _log.debug('%r request %r', task, request)
    tasks.requests[task] = request
    request_call, *request_args = request
    request_handler_name = f'_do_{request_call.replace("-", "_")}'
    try:
        request_handler = getattr(_this_module, request_handler_name)
    except AttributeError:
        _log.error('%r invalid request: %r', task, request)
        # TODO: terminate task somewhat like StopIteration?
    else:
        try:
            request_handler(task, *request_args)
        except Exception as e:
            _log.error('%r call %r execution failed: %r', task, request, e)
            # TODO: inconsistent state? panic?



def _do_clear(task):

    state.terminal.clear()
    tasks.running.append(task)



def _do_print(task, *args):

    state.terminal.print(*args)
    tasks.running.append(task)



def _do_print_at(task, *args):

    state.terminal.print_at(*args)
    tasks.running.append(task)



def _do_sleep(task, seconds):

    wake_at = state.now + seconds
    tasks.waiting_on_time.append(task)
    heapq.heappush(tasks.waiting_on_time_hq, (wake_at, id(task), task))



def _do_read_key(task, priority):

    tasks.waiting_on_key.append(task)
    heapq.heappush(tasks.waiting_on_key_hq, (priority, id(task), task))



def _do_put_key(task, pushed_back_key):

    _process_tasks_waiting_on_key(pushed_back_key)
    tasks.running.append(task)



def _do_run_task(task, child_task):

    tasks.parent[child_task] = task
    tasks.children[task].append(child_task)
    tasks.running.append(child_task)
    tasks.running.append(task)



def _do_wait_task(task):

    child = None
    for candidate, return_value in tasks.terminated:
        if tasks.parent[candidate] is task:
            child = candidate
            break
    if child is not None:
        tasks.responses[task] = (child, return_value)
        del tasks.parent[child]
        tasks.children[task].remove(child)
        _clear_tasks_children(task)
        tasks.running.append(task)
        tasks.terminated.remove((child, return_value))
        _clear_tasks_requests_responses(child)
    else:
        tasks.waiting_on_child.append(task)



def _clear_tasks_children(task):

    if not tasks.children[task]:
        del tasks.children[task]



def _clear_tasks_requests_responses(task):

    for target in (tasks.requests, tasks.responses):
        if task in target:
            del target[task]



def _do_stop_task(task, child_task, keep_running=True):

    if tasks.parent[child_task] is not task:
        raise RuntimeError('cannot kill non-child tasks')

    if child_task in tasks.children:
        for grand_child_task in tasks.children[child_task]:
            _do_stop_task(child_task, grand_child_task, keep_running=False)
            del tasks.parent[grand_child_task]
        del tasks.children[child_task]

    if child_task in tasks.running:
        tasks.running.remove(child_task)
    elif child_task in tasks.waiting_on_child:
        tasks.waiting_on_child.remove(child_task)
    elif child_task in tasks.waiting_on_key:
        tasks.waiting_on_key.remove(child_task)
    elif child_task in tasks.waiting_on_time:
        tasks.waiting_on_time.remove(child_task)
        _clear_tasks_waiting_on_time_hq()
    else:
        terminated = [t for (t, _) in tasks.terminated if t is child_task]
        if terminated:
            _log.error('%r will not stop terminated task %r', task, child_task)
        return

    _clear_tasks_requests_responses(child_task)
    if keep_running:
        tasks.terminated.append((child_task, ('stopped-by', task)))
        tasks.running.append(task)
        _log.info('%r stopped by %r', child_task, task)
    else:
        _log.info('%r stopped from parent %r stop', child_task, task)



_SEPARATOR = '-' * 60

def _do_dump_state(task):

    def _task_status(task):
        if task in tasks.running:
            return 'RR'
        if task in tasks.waiting_on_child:
            return 'WC'
        if task in tasks.waiting_on_key:
            return 'WK'
        if task in tasks.waiting_on_time:
            return 'WT'
        if task in (t for (t, _) in tasks.terminated):
            return 'TT'
        return '??'

    def _task_lines(task, level=0):
        indent = ' ' * 4 * level
        status = _task_status(task)
        _log.critical(f'{status} {indent}{task}')
        if task in tasks.children:
            for child in tasks.children[task]:
                _task_lines(child, level+1)

    _log.critical(_SEPARATOR)
    _task_lines(tasks.top_task)
    _log.critical(_SEPARATOR)
    _log.critical('tasks=%r, state=%r', tasks, state)
    _log.critical(_SEPARATOR)

    if task is not None:
        tasks.running.append(task)



def _clear_tasks_waiting_on_time_hq():

    if not tasks.waiting_on_time:
        tasks.waiting_on_time_hq.clear()



def _run_task_until_request(task):

    request = tasks.requests.get(task)
    response = tasks.responses.get(task)
    if request is not None:
        _log.debug('%r respond %r with %r', task, request, response)
    elif response is not None:
        _log.error('%r respond no request with %r', task, response)
    else:
        _log.debug('%r running', task)
    try:
        return task.running.send(response)
    finally:
        if request:
            del tasks.requests[task]
        if response:
            del tasks.responses[task]



def _process_tasks_waiting_on_key(keyboard_byte=None):

    if keyboard_byte is None:
        keyboard_byte = _read_keyboard(prompt='?')

    if keyboard_byte and tasks.waiting_on_key:
        while tasks.waiting_on_key_hq:
            _, _, key_waiter = heapq.heappop(tasks.waiting_on_key_hq)
            if key_waiter in tasks.waiting_on_key:
                tasks.waiting_on_key.remove(key_waiter)
                tasks.responses[key_waiter] = keyboard_byte
                tasks.running.append(key_waiter)
                _log.info('%r getting key %r', key_waiter, keyboard_byte)
                break



def _process_tasks_waiting_on_time():

    if tasks.waiting_on_time:
        while tasks.waiting_on_time_hq and tasks.waiting_on_time_hq[0][0] < state.now:
            _, _, time_waiter = heapq.heappop(tasks.waiting_on_time_hq)
            if time_waiter in tasks.waiting_on_time:
                tasks.waiting_on_time.remove(time_waiter)
                _clear_tasks_waiting_on_time_hq()
                tasks.running.append(time_waiter)
                _log.info('%r waking up', time_waiter)



def _process_task_completion(task, return_value):

    candidate_parent = tasks.parent.get(task)
    if not candidate_parent:
        _log.error('%r completed with no parent', task)
    if candidate_parent in tasks.waiting_on_child:
        tasks.responses[candidate_parent] = (task, return_value)
        del tasks.parent[task]
        tasks.children[candidate_parent].remove(task)
        _clear_tasks_children(candidate_parent)
        tasks.waiting_on_child.remove(candidate_parent)
        tasks.running.append(candidate_parent)
    else:
        tasks.terminated.append((task, return_value))
    _clear_tasks_requests_responses(task)



def _prompt_context(prompt):

    @contextlib.contextmanager
    def _prompt(prompt):
        col = state.terminal.width - len(prompt)
        row = state.terminal.height - 1
        state.terminal.print_at(col, row, prompt, save_location=True)
        yield
        state.terminal.print_at(col, row, ' '*len(prompt), save_location=True)

    @contextlib.contextmanager
    def _no_prompt():
        yield

    return _prompt(prompt) if prompt else _no_prompt()



def _read_keyboard(prompt=None):

    quit_in_progress = False

    if tasks.waiting_on_time:
        timeout = max(tasks.waiting_on_time_hq[0][0] - state.now, 0)
    else:
        timeout = None
    save_timeout = timeout
    while True:
        actual_prompt = 'QUIT?' if quit_in_progress else prompt
        with _prompt_context(actual_prompt):
            fds, _, _ = select.select(_RD_FDS, _NO_FDS, _NO_FDS, timeout)
        if _STDIN_FD in fds:
            keyboard_byte = os.read(_STDIN_FD, 1)
            if keyboard_byte == b'q':
                if quit_in_progress:
                    raise _PlayerStop()
                else:
                    quit_in_progress = True
                    timeout = None
                continue
            elif quit_in_progress:
                quit_in_progress = False
                timeout = save_timeout
                continue
            elif keyboard_byte == b'D':
                _do_dump_state(None)
                continue
            return keyboard_byte
        elif not quit_in_progress:
            break


# ----------------------------------------------------------------------------
