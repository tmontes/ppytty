# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import collections
import contextlib
import logging
import os
from select import select
import sys

from . _terminal import Terminal



class _PlayerStop(Exception):
    
    pass



_NO_FDS = []


class Player(object):

    def __init__(self, widget):

        self._widget = widget
        self._terminal = None

        self._fd_stdin = sys.stdin.fileno()
        self._rd_fds = [self._fd_stdin]


        self._log = logging.getLogger('player')

        self.keymap = {
            'prev': b'[',
            'next': b']',
            'reload': b'r',
        }


    def run(self):

        with Terminal() as terminal:
            self._terminal = terminal
            try:
                self._run()
            except _PlayerStop:
                pass


    def _run(self):

        running = collections.deque()
        running.append(self._widget)

        terminated = []

        parent = {}
        children = collections.defaultdict(list)

        waiting_on_child = []
        waiting_on_key = collections.deque()

        responses = {}


        while running or waiting_on_child or waiting_on_key or terminated:
            if not running:
                keyboard_byte = self._handle_input(prompt='?')
                if keyboard_byte and waiting_on_key:
                    key_waiter = waiting_on_key.popleft()
                    responses[key_waiter] = keyboard_byte
                    running.append(key_waiter)
                    self._log.info('%r getting key %r', key_waiter, keyboard_byte)
                continue
            widget = running.popleft()
            try:
                response = responses.get(widget)
                try:
                    request = widget.running.send(response)
                finally:
                    if response:
                        del responses[widget]
            except StopIteration as return_:
                self._log.info('%r stopped with %r', widget, return_.value)
                candidate_parent = parent.get(widget)
                if not candidate_parent:
                    if widget is not self._widget:
                        raise RuntimeError(f'{widget} stopped with no parent')
                    continue
                if candidate_parent in waiting_on_child:
                    responses[candidate_parent] = (widget, return_.value)
                    del parent[widget]
                    children[candidate_parent].remove(widget)
                    waiting_on_child.remove(candidate_parent)
                    running.append(candidate_parent)
                else:
                    terminated.append((widget, return_.value))
            else:
                what, *args = request
                self._log.info('%r %r %r', widget, what, args)
                if what == 'get-keymap':
                    responses[widget] = self.keymap
                    running.append(widget)
                elif what == 'clear':
                    self._terminal.clear()
                    running.append(widget)
                elif what == 'print':
                    self._terminal.print(*args)
                    running.append(widget)
                elif what == 'read-key':
                    waiting_on_key.append(widget)
                elif what == 'run-widget':
                    child_widget = args[0]
                    parent[child_widget] = widget
                    children[widget].append(child_widget)
                    running.append(child_widget)
                    running.append(widget)
                elif what == 'wait-widget':
                    child = None
                    for candidate, return_value in terminated:
                        if parent[candidate] is widget:
                            child = candidate
                            break
                    if child is not None:
                        responses[widget] = (child, return_value)
                        del parent[child]
                        children[widget].remove(child)
                        running.append(widget)
                        terminated.remove((child, return_value))
                    else:
                        waiting_on_child.append(widget)
                else:
                    raise ValueError(f'unhandled action {what!r}')

        self._handle_input(prompt='DONE', wait=True)


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
