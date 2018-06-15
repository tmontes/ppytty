# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import contextlib
import heapq
import os
import select
import sys
import time

from . log import log
from . import handlers
from . import common
from . state import tasks, state
from . terminal import Terminal



class _PlayerStop(Exception):

    pass



_STDIN_FD = sys.stdin.fileno()
_RD_FDS = [_STDIN_FD]
_NO_FDS = []



def run(task, post_prompt='[COMPLETED]'):

    # TODO: default to disable logging so as not to require callers to
    #       do that themselves if they don't care; this avoids spurious
    #       sys.stderr output resulting from messages >= warning from the
    #       default standard library's logging module.

    with Terminal() as terminal:
        state.terminal = terminal
        try:
            scheduler(task)
            while post_prompt:
                _ = _read_keyboard(prompt=post_prompt)
        except _PlayerStop:
            pass



def scheduler(top_task):

    tasks.top_task = top_task
    tasks.running.append(top_task)

    while (tasks.running or tasks.waiting_on_child or tasks.waiting_on_key or
           tasks.waiting_on_time or tasks.terminated):
        state.now = time.time()
        if not tasks.running:
            process_tasks_waiting_on_key()
            process_tasks_waiting_on_time()
            continue
        task = tasks.running.popleft()
        try:
            request = run_task_until_request(task)
        except StopIteration as return_:
            log.info('%r completed with %r', task, return_.value)
            if task is top_task:
                continue
            process_task_completion(task, return_.value)
        else:
            process_task_request(task, request)



def process_task_request(task, request):

    log.debug('%r request %r', task, request)
    tasks.requests[task] = request
    request_call, *request_args = request
    request_handler_name = request_call.replace("-", "_")
    try:
        request_handler = getattr(handlers, request_handler_name)
    except AttributeError:
        log.error('%r invalid request: %r', task, request)
        # TODO: terminate task somewhat like StopIteration?
    else:
        try:
            request_handler(task, *request_args)
        except Exception as e:
            log.error('%r call %r execution failed: %r', task, request, e)
            # TODO: inconsistent state? panic?



def run_task_until_request(task):

    request = tasks.requests.get(task)
    response = tasks.responses.get(task)
    if request is not None:
        log.debug('%r respond %r with %r', task, request, response)
    elif response is not None:
        log.error('%r respond no request with %r', task, response)
    else:
        log.debug('%r running', task)
    try:
        return task.running.send(response)
    finally:
        if request:
            del tasks.requests[task]
        if response:
            del tasks.responses[task]



def process_tasks_waiting_on_key(keyboard_byte=None):

    if keyboard_byte is None:
        keyboard_byte = _read_keyboard(prompt='?')

    if keyboard_byte and tasks.waiting_on_key:
        while tasks.waiting_on_key_hq:
            _, _, key_waiter = heapq.heappop(tasks.waiting_on_key_hq)
            if key_waiter in tasks.waiting_on_key:
                tasks.waiting_on_key.remove(key_waiter)
                tasks.responses[key_waiter] = keyboard_byte
                tasks.running.append(key_waiter)
                log.info('%r getting key %r', key_waiter, keyboard_byte)
                break



def process_tasks_waiting_on_time():

    if tasks.waiting_on_time:
        while tasks.waiting_on_time_hq and tasks.waiting_on_time_hq[0][0] < state.now:
            _, _, time_waiter = heapq.heappop(tasks.waiting_on_time_hq)
            if time_waiter in tasks.waiting_on_time:
                tasks.waiting_on_time.remove(time_waiter)
                common.clear_tasks_waiting_on_time_hq()
                tasks.running.append(time_waiter)
                log.info('%r waking up', time_waiter)



def process_task_completion(task, return_value):

    candidate_parent = tasks.parent.get(task)
    if not candidate_parent:
        log.error('%r completed with no parent', task)
    if candidate_parent in tasks.waiting_on_child:
        tasks.responses[candidate_parent] = (task, return_value)
        del tasks.parent[task]
        tasks.children[candidate_parent].remove(task)
        common.clear_tasks_children(candidate_parent)
        tasks.waiting_on_child.remove(candidate_parent)
        tasks.running.append(candidate_parent)
    else:
        tasks.terminated.append((task, return_value))
    common.clear_tasks_requests_responses(task)



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
                handlers.dump_state(None)
                continue
            return keyboard_byte
        elif not quit_in_progress:
            break


# ----------------------------------------------------------------------------
