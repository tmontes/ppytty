# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import os
import sys
import termios

import blessings



class Terminal(object):

    def __init__(self):

        self._fail_if_not_tty(sys.stdin)
        self._fail_if_not_tty(sys.stdout)

        self._term = blessings.Terminal()
        self._outfd = sys.stdout.fileno()


    def _fail_if_not_tty(self, stream):

        if not stream.isatty():
            raise RuntimeError(f'{stream.name} must be a TTY')


    def _write(self, string):

        self._term.stream.write(string)


    def _termios_settings(self, activate=True):

        tc_attrs = termios.tcgetattr(self._outfd)
        settings = termios.ICANON | termios.ECHO
        if activate:
            tc_attrs[3] &= ~settings
        else:
            tc_attrs[3] |= settings
        termios.tcsetattr(self._outfd, termios.TCSANOW, tc_attrs)


    def __enter__(self):

        self._write(self._term.enter_fullscreen)
        self._write(self._term.hide_cursor)
        self._termios_settings(activate=True)
        return self


    def __exit__(self, exc_type, exc_value, traceback):

        self._termios_settings(activate=False)
        self._write(self._term.normal_cursor)
        self._write(self._term.exit_fullscreen)
        # TODO: Handle exceptions or let them through?


    @property
    def width(self):

        return self._term.width


    @property
    def height(self):

        return self._term.height


    def print(self, string):

        self._term.stream.write(string + '\n')
        self._term.stream.flush()


    def print_at(self, col, row, string):

        with self._term.location(col, row):
            self._term.stream.write(string)
            self._term.stream.flush()


# ----------------------------------------------------------------------------
