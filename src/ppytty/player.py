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

from . terminal import Terminal



class _PlayerStop(Exception):
    
    pass



_log = logging.getLogger('player')

_STDIN_FD = sys.stdin.fileno()
_RD_FDS = [_STDIN_FD]
_NO_FDS = []



def run(task, post_prompt='[COMPLETED]'):

    # TODO: default to disable logging so as not to require callers to
    #       do that themselves if they don't care; this avoids spurious
    #       sys.stderr output resulting from messages >= warning from the
    #       default standard library's logging module.

    with Terminal() as terminal:
        try:
            _run(task, terminal)
            while post_prompt:
                _handle_input(terminal, prompt=post_prompt, wait=True)
        except _PlayerStop:
            pass



def _run(top_task, terminal):

    running = collections.deque()
    running.append(top_task)

    terminated = []

    parent = {}
    children = collections.defaultdict(list)

    waiting_on_child = []
    waiting_on_key = collections.deque()
    waiting_on_time = []

    responses = {}


    while running or waiting_on_child or waiting_on_key or waiting_on_time or terminated:
        now = time.time()
        if not running:
            keyboard_byte = _handle_input(terminal, prompt='?')
            if keyboard_byte and waiting_on_key:
                key_waiter = waiting_on_key.popleft()
                responses[key_waiter] = keyboard_byte
                running.append(key_waiter)
                _log.info('%r getting key %r', key_waiter, keyboard_byte)
            if waiting_on_time and waiting_on_time[0][0] < now:
                _, time_waiter = heapq.heappop(waiting_on_time)
                running.append(time_waiter)
                _log.info('%r waking up', time_waiter)
            continue
        task = running.popleft()
        try:
            response = responses.get(task)
            try:
                request = task.running.send(response)
            finally:
                if response:
                    del responses[task]
        except StopIteration as return_:
            _log.info('%r stopped with %r', task, return_.value)
            candidate_parent = parent.get(task)
            if not candidate_parent:
                if task is not top_task:
                    _log.error('%r stopped with no parent', task)
                continue
            if candidate_parent in waiting_on_child:
                responses[candidate_parent] = (task, return_.value)
                del parent[task]
                children[candidate_parent].remove(task)
                waiting_on_child.remove(candidate_parent)
                running.append(candidate_parent)
            else:
                terminated.append((task, return_.value))
        else:
            what, *args = request
            _log.info('%r %r %r', task, what, args)
            if what == 'clear':
                terminal.clear()
                running.append(task)
            elif what == 'print':
                terminal.print(*args)
                running.append(task)
            elif what == 'sleep':
                wake_at = now + args[0]
                heapq.heappush(waiting_on_time, (wake_at, task))
            elif what == 'read-key':
                waiting_on_key.append(task)
            elif what == 'run-task':
                child_task = args[0]
                parent[child_task] = task
                children[task].append(child_task)
                running.append(child_task)
                running.append(task)
            elif what == 'wait-task':
                child = None
                for candidate, return_value in terminated:
                    if parent[candidate] is task:
                        child = candidate
                        break
                if child is not None:
                    responses[task] = (child, return_value)
                    del parent[child]
                    children[task].remove(child)
                    running.append(task)
                    terminated.remove((child, return_value))
                else:
                    waiting_on_child.append(task)
            else:
                _log.error('%r invalid request: %r', task, what)
                # TODO: terminate task somewhat like StopIteration



def _prompt_context(terminal, prompt):

    @contextlib.contextmanager
    def _prompt(prompt):
        col = terminal.width - len(prompt)
        row = terminal.height - 1
        terminal.print_at(col, row, prompt)
        yield
        terminal.print_at(col, row, ' '*len(prompt))

    @contextlib.contextmanager
    def _no_prompt():
        yield

    return _prompt(prompt) if prompt else _no_prompt()



def _handle_input(terminal=None, prompt=None, wait=False):

    quit_in_progress = False

    timeout = None if wait else 0.02
    while True:
        actual_prompt = 'QUIT?' if quit_in_progress else prompt
        with _prompt_context(terminal, actual_prompt):
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
            return keyboard_byte
        elif not quit_in_progress:
            return


# ----------------------------------------------------------------------------
