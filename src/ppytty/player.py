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



_log = logging.getLogger('player')

_STDIN_FD = sys.stdin.fileno()
_RD_FDS = [_STDIN_FD]
_NO_FDS = []

_tasks = types.SimpleNamespace()



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

    _tasks.running = collections.deque()
    _tasks.running.append(top_task)

    _tasks.terminated = []

    _tasks.parent = {}
    _tasks.children = collections.defaultdict(list)

    _tasks.waiting_on_child = []
    _tasks.waiting_on_key = collections.deque()
    _tasks.waiting_on_time = []

    _tasks.responses = {}


    while (_tasks.running or _tasks.waiting_on_child or _tasks.waiting_on_key or
           _tasks.waiting_on_time or _tasks.terminated):
        now = time.time()
        if not _tasks.running:
            keyboard_byte = _handle_input(terminal, prompt='?')
            if keyboard_byte and _tasks.waiting_on_key:
                key_waiter = _tasks.waiting_on_key.popleft()
                _tasks.responses[key_waiter] = keyboard_byte
                _tasks.running.append(key_waiter)
                _log.info('%r getting key %r', key_waiter, keyboard_byte)
            if _tasks.waiting_on_time and _tasks.waiting_on_time[0][0] < now:
                _, time_waiter = heapq.heappop(_tasks.waiting_on_time)
                _tasks.running.append(time_waiter)
                _log.info('%r waking up', time_waiter)
            continue
        task = _tasks.running.popleft()
        try:
            response = _tasks.responses.get(task)
            try:
                request = task.running.send(response)
            finally:
                if response:
                    del _tasks.responses[task]
        except StopIteration as return_:
            _log.info('%r stopped with %r', task, return_.value)
            candidate_parent = _tasks.parent.get(task)
            if not candidate_parent:
                if task is not top_task:
                    _log.error('%r stopped with no parent', task)
                continue
            if candidate_parent in _tasks.waiting_on_child:
                _tasks.responses[candidate_parent] = (task, return_.value)
                del _tasks.parent[task]
                _tasks.children[candidate_parent].remove(task)
                _tasks.waiting_on_child.remove(candidate_parent)
                _tasks.running.append(candidate_parent)
            else:
                _tasks.terminated.append((task, return_.value))
        else:
            what, *args = request
            _log.info('%r %r %r', task, what, args)
            if what == 'clear':
                terminal.clear()
                _tasks.running.append(task)
            elif what == 'print':
                terminal.print(*args)
                _tasks.running.append(task)
            elif what == 'sleep':
                wake_at = now + args[0]
                heapq.heappush(_tasks.waiting_on_time, (wake_at, task))
            elif what == 'read-key':
                _tasks.waiting_on_key.append(task)
            elif what == 'run-task':
                child_task = args[0]
                _tasks.parent[child_task] = task
                _tasks.children[task].append(child_task)
                _tasks.running.append(child_task)
                _tasks.running.append(task)
            elif what == 'wait-task':
                child = None
                for candidate, return_value in _tasks.terminated:
                    if _tasks.parent[candidate] is task:
                        child = candidate
                        break
                if child is not None:
                    _tasks.responses[task] = (child, return_value)
                    del _tasks.parent[child]
                    _tasks.children[task].remove(child)
                    _tasks.running.append(task)
                    _tasks.terminated.remove((child, return_value))
                else:
                    _tasks.waiting_on_child.append(task)
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
