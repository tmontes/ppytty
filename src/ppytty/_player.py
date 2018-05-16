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

        waiting_on_child = collections.defaultdict(list)
        childs_waited_on = {}

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
                request = widget.running.send(response)
                responses[widget] = None
            except StopIteration:
                self._log.info('%r stopped', widget)
                waiting_parent = childs_waited_on.get(widget)
                if waiting_parent:
                    waited_children = waiting_on_child[waiting_parent]
                    waited_children.remove(widget)
                    del childs_waited_on[widget]
                    if not waited_children:
                        del waiting_on_child[waiting_parent]
                        running.append(waiting_parent)
                elif widget is not self._widget:
                    terminated.append(widget)
            else:
                what, *args = request
                self._log.info('%r %r %r', widget, what, args)
                if what == 'clear':
                    self._terminal.clear()
                    running.append(widget)
                elif what == 'print':
                    self._terminal.print(*args)
                    running.append(widget)
                elif what == 'read-key':
                    waiting_on_key.append(widget)
                elif what == 'create-widgets':
                    for child_widget in args[0]:
                        running.append(child_widget)
                    running.append(widget)
                elif what == 'wait-widgets':
                    for child_widget in args[0]:
                        if child_widget in terminated:
                            terminated.remove(child_widget)
                        else:
                            waiting_on_child[widget].append(child_widget)
                            if child_widget in childs_waited_on:
                                raise RuntimeError(f'double-wait on child')
                            childs_waited_on[child_widget] = widget
                else:
                    raise ValueError(f'unhandled action {what!r}')

        self._handle_input(prompt='DONE', wait=True)



    KEY_TO_ACTIONS = {
        b']': ('move', 'next_sub_step', 'last!'),
        b'[': ('move', 'prev_sub_step', 'first!'),
        b'}': ('move', 'next_step', 'LAST!'),
        b'{': ('move', 'prev_step', 'FIRST!'),
        b'r': ('move', 'current_step', '<reload current failed>'),
        b'1': ('move', 'first_step', '<go to first failed>'),
        b'0': ('move', 'last_step', '<go to last failed>'),
    }

    def _next_step(self):

        fail_prompt = None

        while True:
            prompt = fail_prompt if fail_prompt else 'ISW'
            keyboard_byte = self._handle_input(prompt=prompt, wait=True)
            fail_prompt = None
            try:
                action, *args = self.KEY_TO_ACTIONS[keyboard_byte]
            except KeyError:
                continue
            if action == 'move':
                next_callable, fail_msg = args
                try:
                    return getattr(self._script, next_callable)()
                except AttributeError:
                    pass
                except ScriptLimit:
                    fail_prompt = fail_msg


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
