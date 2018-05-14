# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import contextlib
import os
from select import select
import sys

from . _terminal import Terminal



class Player(object):

    def __init__(self, script):

        self._script = script

        self._terminal = None

        self._fd_stdin = sys.stdin.fileno()
        self._readables = [self._fd_stdin]
        self._dont_care = []


    _MOVEMENTS = {
        'next': lambda s, i: i+1,
        'prev': lambda s, i: i-1,
        'first': lambda s, i: 0,
        'last': lambda s, i: len(s)-1,
        'redo': lambda s, i: i,
    }

    def run(self):

        step_index = 0
        num_steps = len(self._script)

        with Terminal() as terminal:
            self._terminal = terminal
            while step_index < num_steps:
                step = self._script[step_index]
                where_to = self._run_step(step)
                try:
                    where_to_callable = self._MOVEMENTS[where_to]
                except KeyError:
                    if where_to == 'quit':
                        break
                else:
                    step_index = where_to_callable(self._script, step_index)
            while True:
                keyboard_byte = self._handle_input(prompt='EXIT', wait=True)
                if self.KEY_TO_ACTIONS.get(keyboard_byte) == 'quit':
                    break


    KEY_TO_ACTIONS = {
        b']': 'next',
        b'[': 'prev',
        b'r': 'redo',
        b'q': 'quit',
    }

    def _run_step(self, step):

        for who, when, what, *args in step:
            if what == 'print':
                self._terminal.print(*args)
            elif what == 'wait':
                result = self._handle_input(prompt='what=wait', wait=True)
            else:
                raise ValueError(f'unknown action {action!r}')
        result = self._handle_input(prompt='ISW', wait=True)
        return self.KEY_TO_ACTIONS.get(result, '')


    @contextlib.contextmanager
    def _prompt(self, prompt):

        col = self._terminal.width - len(prompt)
        row = self._terminal.height - 1
        self._terminal.print_at(col, row, prompt)
        yield
        self._terminal.print_at(col, row, ' '*len(prompt))


    def _handle_input(self, prompt=None, wait=False):

        timeout = None if wait else 0.02
        cm = self._prompt(prompt) if prompt else contextlib.suppress()
        with cm:
            fds, _, _ = select(self._readables, self._dont_care, self._dont_care, timeout)
        if self._fd_stdin in fds:
            keyboard_byte = os.read(self._fd_stdin, 1)
            return keyboard_byte


# ----------------------------------------------------------------------------
