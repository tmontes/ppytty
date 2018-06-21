# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import functools
import os
import sys
import termios

import blessings

from . import window


class Terminal(object):

    def __init__(self, in_file=sys.stdin, out_file=sys.stdout, kind=None,
                 left=0, top=0, width=None, height=None, bg=None,
                 encoding='UTF-8'):

        self._fail_if_not_tty(in_file)
        self._fail_if_not_tty(out_file)

        self._in_fd = in_file.fileno()
        self._out_fd = out_file.fileno()

        self._bt = blessings.Terminal(kind=kind, stream=out_file)
        self._encoding = encoding

        width = width if width else self._bt.width
        height = height if height else self._bt.height
        self._window = window.Window(left, top, width, height, bg)

        # Speed up sub-attribute access with these attributes.
        self._bt_clear = self._bt.clear
        self._bt_save = self._bt.save
        self._bt_restore = self._bt.restore
        self._bt_move = self._bt.move
        self._window_clear = self._window.clear
        self._window_feed = self._window.feed
        self._window_render = self._window.render
        self._os_write_out_fd = functools.partial(os.write, self._out_fd)


    def _fail_if_not_tty(self, stream):

        if not stream.isatty():
            raise RuntimeError(f'{stream!r} must be a TTY')


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


    def _write(self, *text):

        self._os_write_out_fd(''.join(text).encode(self._encoding))


    def __enter__(self):

        self._write(self._bt.enter_fullscreen, self._bt.hide_cursor)
        self._termios_settings(activate=True)
        return self


    def __exit__(self, exc_type, exc_value, traceback):

        self._termios_settings(activate=False)
        self._write(self._bt.normal_cursor, self._bt.exit_fullscreen)
        # TODO: Reset colors?
        # TODO: Handle exceptions or let them through?


    @property
    def width(self):

        return self._bt.width


    @property
    def height(self):

        return self._bt.height


    def direct_clear(self):

        self._write(self._bt_clear)


    def direct_print(self, text, x=None, y=None, save_location=False):

        positioning = not (x is None or y is None)
        self._write(
            self._bt_save if save_location else '',
            self._bt_move(y, x) if positioning else '',
            text,
            '\n' if not positioning else '',
            self._bt_restore if save_location else '',
        )

    def clear(self):

        self._window_clear()


    def feed(self, data):

        self._window_feed(data)


    def render(self, full=False):

        data = self._window_render(bt=self._bt, full=full, encoding=self._encoding)
        self._os_write_out_fd(data)


# ----------------------------------------------------------------------------
