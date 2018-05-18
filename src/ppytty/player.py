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
from select import select
import sys
import time

from . terminal import Terminal



class _PlayerStop(Exception):
    
    pass



_NO_FDS = []


class Player(object):

    def __init__(self, task, post_prompt='[COMPLETED]'):

        # TODO: default to disable logging so as not to require callers to
        #       do that themselves if they don't care; this avoids spurious
        #       sys.stderr output resulting from messages >= warning from the
        #       default standard library's logging module.

        self._task = task
        self._post_prompt = post_prompt

        self._terminal = None

        self._fd_stdin = sys.stdin.fileno()
        self._rd_fds = [self._fd_stdin]

        self._log = logging.getLogger('player')


    def run(self):

        with Terminal() as terminal:
            self._terminal = terminal
            try:
                self._run()
            except _PlayerStop:
                pass


    def _run(self):

        running = collections.deque()
        running.append(self._task)

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
                keyboard_byte = self._handle_input(prompt='?')
                if keyboard_byte and waiting_on_key:
                    key_waiter = waiting_on_key.popleft()
                    responses[key_waiter] = keyboard_byte
                    running.append(key_waiter)
                    self._log.info('%r getting key %r', key_waiter, keyboard_byte)
                if waiting_on_time and waiting_on_time[0][0] < now:
                    _, time_waiter = heapq.heappop(waiting_on_time)
                    running.append(time_waiter)
                    self._log.info('%r waking up', time_waiter)
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
                self._log.info('%r stopped with %r', task, return_.value)
                candidate_parent = parent.get(task)
                if not candidate_parent:
                    if task is not self._task:
                        self._log.error('%r stopped with no parent', task)
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
                self._log.info('%r %r %r', task, what, args)
                if what == 'clear':
                    self._terminal.clear()
                    running.append(task)
                elif what == 'print':
                    self._terminal.print(*args)
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
                    self._log.error('%r invalid request: %r', task, what)
                    # TODO: terminate task somewhat like StopIteration

        while self._post_prompt:
            self._handle_input(prompt=self._post_prompt, wait=True)


    def _prompt_context(self, prompt):

        @contextlib.contextmanager
        def _prompt(prompt):
            col = self._terminal.width - len(prompt)
            row = self._terminal.height - 1
            self._terminal.print_at(col, row, prompt)
            yield
            self._terminal.print_at(col, row, ' '*len(prompt))

        @contextlib.contextmanager
        def _no_prompt():
            yield

        return _prompt(prompt) if prompt else _no_prompt()


    def _handle_input(self, prompt=None, wait=False):

        quit_in_progress = False

        timeout = None if wait else 0.02
        while True:
            actual_prompt = 'QUIT?' if quit_in_progress else prompt
            with self._prompt_context(actual_prompt):
                fds, _, _ = select(self._rd_fds, _NO_FDS, _NO_FDS, timeout)
            if self._fd_stdin in fds:
                keyboard_byte = os.read(self._fd_stdin, 1)
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
