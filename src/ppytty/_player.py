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

from . _script import ScriptLimit
from . _terminal import Terminal



class _PlayerStop(Exception):
    
    pass



_NO_FDS = []


class Player(object):

    def __init__(self, script):

        self._script = script
        self._terminal = None

        self._fd_stdin = sys.stdin.fileno()
        self._rd_fds = [self._fd_stdin]

        self._focus = None


    def run(self):

        step = self._script.first_step()

        with Terminal() as terminal:
            self._terminal = terminal
            while step:
                try:
                    self._run_step(step)
                    step = self._next_step()
                except _PlayerStop:
                    step = None


    def _run_step(self, step):

        self._terminal.clear()
        for who, when, what, *args in step:
            if what == 'print':
                self._terminal.print(*args)
            elif what == 'wait':
                result = self._handle_input(prompt='what=wait', wait=True)
            else:
                raise ValueError(f'unknown action {what!r}')


    KEY_TO_ACTIONS = {
        b']': ('move', 'next_step', 'LAST!'),
        b'[': ('move', 'prev_step', 'FIRST!'),
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
                if self._focus is None:
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


# ----------------------------------------------------------------------------
