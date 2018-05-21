# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import collections
import contextlib
import heapq
import logging
import os
import select
import sys
import time
import types

from . terminal import Terminal



class _PlayerStop(Exception):
    
    pass



_log = logging.getLogger('runner')

_STDIN_FD = sys.stdin.fileno()
_RD_FDS = [_STDIN_FD]
_NO_FDS = []

_tasks = types.SimpleNamespace()
_state = types.SimpleNamespace()

_this_module = sys.modules[__name__]



def run(task, post_prompt='[COMPLETED]'):

    # TODO: default to disable logging so as not to require callers to
    #       do that themselves if they don't care; this avoids spurious
    #       sys.stderr output resulting from messages >= warning from the
    #       default standard library's logging module.

    with Terminal() as terminal:
        _state.terminal = terminal
        try:
            _run(task)
            while post_prompt:
                _ = _read_keyboard(prompt=post_prompt, wait=True)
        except _PlayerStop:
            pass



def _run(top_task):

    _tasks.top_task = top_task
    _tasks.running = collections.deque()
    _tasks.running.append(top_task)

    _tasks.terminated = []

    _tasks.parent = {}
    _tasks.children = collections.defaultdict(list)

    _tasks.waiting_on_child = []
    _tasks.waiting_on_key = collections.deque()
    _tasks.waiting_on_time = []
    _tasks.waiting_on_time_hq = []

    _tasks.requests = {}
    _tasks.responses = {}


    while (_tasks.running or _tasks.waiting_on_child or _tasks.waiting_on_key or
           _tasks.waiting_on_time or _tasks.terminated):
        _state.now = time.time()
        if not _tasks.running:
            _process_tasks_waiting_on_key()
            _process_tasks_waiting_on_time()
            continue
        task = _tasks.running.popleft()
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
    _tasks.requests[task] = request
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

    _state.terminal.clear()
    _tasks.running.append(task)



def _do_print(task, *args):

    _state.terminal.print(*args)
    _tasks.running.append(task)



def _do_sleep(task, seconds):

    wake_at = _state.now + seconds
    _tasks.waiting_on_time.append(task)
    heapq.heappush(_tasks.waiting_on_time_hq, (wake_at, task))



def _do_read_key(task):

    _tasks.waiting_on_key.append(task)



def _do_run_task(task, child_task):

    _tasks.parent[child_task] = task
    _tasks.children[task].append(child_task)
    _tasks.running.append(child_task)
    _tasks.running.append(task)



def _do_wait_task(task):

    child = None
    for candidate, return_value in _tasks.terminated:
        if _tasks.parent[candidate] is task:
            child = candidate
            break
    if child is not None:
        _tasks.responses[task] = (child, return_value)
        del _tasks.parent[child]
        _tasks.children[task].remove(child)
        _clear_tasks_children(task)
        _tasks.running.append(task)
        _tasks.terminated.remove((child, return_value))
        _clear_tasks_requests_responses(child)
    else:
        _tasks.waiting_on_child.append(task)



def _clear_tasks_children(task):

    if not _tasks.children[task]:
        del _tasks.children[task]



def _clear_tasks_requests_responses(task):

    for target in (_tasks.requests, _tasks.responses):
        if task in target:
            del target[task]



def _do_stop_task(task, child_task, keep_running=True):

    if _tasks.parent[child_task] is not task:
        raise RuntimeError('cannot kill non-child tasks')

    if child_task in _tasks.children:
        for grand_child_task in _tasks.children[child_task]:
            _do_stop_task(child_task, grand_child_task, keep_running=False)

    if child_task in _tasks.running:
        _tasks.running.remove(child_task)
    elif child_task in _tasks.waiting_on_child:
        _tasks.waiting_on_child.remove(child_task)
    elif child_task in _tasks.waiting_on_key:
        _tasks.waiting_on_key.remove(child_task)
    elif child_task in _tasks.waiting_on_time:
        _tasks.waiting_on_time.remove(child_task)
        _clear_tasks_waiting_on_time_hq()
    else:
        terminated = [t for (t, _) in _tasks.terminated if t is child_task]
        if terminated:
            _log.error('%r will not stop terminated task %r', task, child_task)
        return

    _clear_tasks_requests_responses(child_task)
    if keep_running:
        _tasks.terminated.append((child_task, ('stopped-by', task)))
        _tasks.running.append(task)
        _log.info('%r stopped by %r', child_task, task)
    else:
        del _tasks.parent[child_task]
        _tasks.children[task].remove(child_task)
        _clear_tasks_children(task)
        _log.info('%r stopped from parent %r stop', child_task, task)



_SEPARATOR = '-' * 60

def _do_dump_state(top_task):

    def _task_status(task):
        if task in _tasks.running:
            return 'RR'
        elif task in _tasks.waiting_on_child:
            return 'WC'
        elif task in _tasks.waiting_on_key:
            return 'WK'
        elif task in _tasks.waiting_on_time:
            return 'WT'
        elif task in (t for (t, _) in _tasks.terminated):
            return 'TT'
        else:
            return '??'

    def _task_lines(task, level=0):
        indent = ' ' * 4 * level
        status = _task_status(task)
        _log.critical(f'{status} {indent}{task}')
        if task in _tasks.children:
            for child in _tasks.children[task]:
                _task_lines(child, level+1)

    _log.critical(_SEPARATOR)
    _task_lines(top_task)
    _log.critical(_SEPARATOR)
    _log.critical('tasks=%r, state=%r', _tasks, _state)
    _log.critical(_SEPARATOR)



def _clear_tasks_waiting_on_time_hq():

    if not _tasks.waiting_on_time:
        _tasks.waiting_on_time_hq.clear()



def _run_task_until_request(task):

    request = _tasks.requests.get(task)
    response = _tasks.responses.get(task)
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
            del _tasks.requests[task]
        if response:
            del _tasks.responses[task]



def _process_tasks_waiting_on_key():

    keyboard_byte = _read_keyboard(prompt='?')
    if keyboard_byte and _tasks.waiting_on_key:
        key_waiter = _tasks.waiting_on_key.popleft()
        _tasks.responses[key_waiter] = keyboard_byte
        _tasks.running.append(key_waiter)
        _log.info('%r getting key %r', key_waiter, keyboard_byte)



def _process_tasks_waiting_on_time():

    if _tasks.waiting_on_time:
        while _tasks.waiting_on_time_hq and _tasks.waiting_on_time_hq[0][0] < _state.now:
            _, time_waiter = heapq.heappop(_tasks.waiting_on_time_hq)
            if time_waiter in _tasks.waiting_on_time:
                _tasks.waiting_on_time.remove(time_waiter)
                _clear_tasks_waiting_on_time_hq()
                _tasks.running.append(time_waiter)
                _log.info('%r waking up', time_waiter)



def _process_task_completion(task, return_value):

    candidate_parent = _tasks.parent.get(task)
    if not candidate_parent:
        _log.error('%r completed with no parent', task)
    if candidate_parent in _tasks.waiting_on_child:
        _tasks.responses[candidate_parent] = (task, return_value)
        del _tasks.parent[task]
        _tasks.children[candidate_parent].remove(task)
        _clear_tasks_children(candidate_parent)
        _tasks.waiting_on_child.remove(candidate_parent)
        _tasks.running.append(candidate_parent)
    else:
        _tasks.terminated.append((task, return_value))
    _clear_tasks_requests_responses(task)



def _prompt_context(prompt):

    @contextlib.contextmanager
    def _prompt(prompt):
        col = _state.terminal.width - len(prompt)
        row = _state.terminal.height - 1
        _state.terminal.print_at(col, row, prompt)
        yield
        _state.terminal.print_at(col, row, ' '*len(prompt))

    @contextlib.contextmanager
    def _no_prompt():
        yield

    return _prompt(prompt) if prompt else _no_prompt()



def _read_keyboard(prompt=None, wait=False):

    quit_in_progress = False

    timeout = None if wait else 0.02
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
                continue
            elif quit_in_progress:
                quit_in_progress = False
                continue
            elif keyboard_byte == b'D':
                _do_dump_state(_tasks.top_task)
                continue
            return keyboard_byte
        elif not quit_in_progress:
            return


# ----------------------------------------------------------------------------
