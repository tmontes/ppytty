# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import sys
import termios

import blessings



class Terminal(object):

    def __init__(self, in_file=sys.stdin, out_file=sys.stdout):

        self._fail_if_not_tty(in_file)
        self._fail_if_not_tty(out_file)

        self._term = blessings.Terminal()
        self._in_fd = in_file.fileno()
        self._out_fd = out_file.fileno()

        self._write = self._term.stream.write
        self._flush = self._term.stream.flush


    def _fail_if_not_tty(self, stream):

        if not stream.isatty():
            raise RuntimeError(f'{stream.name} must be a TTY')


    @property
    def in_fd(self):

        return self._in_fd


    @property
    def out_fd(self):

        return self._out_fd


    def _termios_settings(self, activate=True):

        tc_attrs = termios.tcgetattr(self._out_fd)
        settings = termios.ICANON | termios.ECHO | termios.ISIG
        if activate:
            tc_attrs[3] &= ~settings
        else:
            tc_attrs[3] |= settings
        termios.tcsetattr(self._out_fd, termios.TCSANOW, tc_attrs)


    def __enter__(self):

        self._write(self._term.enter_fullscreen)
        self._write(self._term.hide_cursor)
        self._termios_settings(activate=True)
        return self


    def __exit__(self, exc_type, exc_value, traceback):

        self._termios_settings(activate=False)
        self._write(self._term.normal_cursor)
        self._write(self._term.exit_fullscreen)
        # TODO: Reset colors?
        # TODO: Handle exceptions or let them through?


    @property
    def width(self):

        return self._term.width


    @property
    def height(self):

        return self._term.height


    def clear(self):

        self._write(self._term.clear)


    def print(self, string):

        self._write(string + '\n')
        self._flush()


    def print_at(self, col, row, string, save_location=False):

        if not save_location:
            self._write(self._term.move(row, col) + string)
        else:
            with self._term.location(col, row):
                self._write(string)
        self._flush()


# ----------------------------------------------------------------------------
