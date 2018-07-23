# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import collections
import functools

import blessings

from . import hw
from . import window


class Terminal(object):

    def __init__(self, in_file=None, out_file=None, kind=None, bg=None,
                 encoding='UTF-8'):

        in_file = hw.sys_stdin if in_file is None else in_file
        out_file = hw.sys_stdout if out_file is None else out_file

        self._in_fd = in_file.fileno()
        self._out_fd = out_file.fileno()
        self._ttyname = self._common_tty_name(self._in_fd, self._out_fd)

        self._bt = blessings.Terminal(kind=kind, stream=out_file)
        self._encoding = encoding

        self._window = window.Window(self, 0, 0, 1.0, 1.0, bg=bg)
        self._window.title = 'ppytty'

        self.input_buffer = collections.deque()

        # Speed up sub-attribute access with these attributes.
        self._bt_clear = self._bt.clear
        self._bt_save = self._bt.save
        self._bt_restore = self._bt.restore
        self._bt_move = self._bt.move
        self._window_clear = self._window.clear
        self._window_feed = self._window.feed
        self._window_render = self._window.render
        self._os_write_out_fd = functools.partial(hw.os_write_all, self._out_fd)


    def _common_tty_name(self, *fds):

        try:
            tty_names = {hw.os_ttyname(fd) for fd in fds}
        except OSError:
            raise RuntimeError(f'terminal I/O requires TTYs')

        if len(tty_names) != 1:
            raise RuntimeError('terminal I/O must be on the same TTY')

        return tty_names.pop()


    def __repr__(self):

        return f'<Terminal {self._ttyname} {hex(id(self))}>'


    @property
    def in_fd(self):

        return self._in_fd


    @property
    def out_fd(self):

        return self._out_fd


    @property
    def bt(self):

        # self is self._window's parent; thus it needs to expose self.bt.
        return self._bt


    @property
    def window(self):

        # Windows created via traps need parents: Terminal.window is that.

        return self._window


    def _termios_settings(self, activate=True):

        tc_attrs = hw.termios_tcgetattr(self._out_fd)
        settings = hw.termios_ICANON | hw.termios_ECHO | hw.termios_ISIG
        if activate:
            tc_attrs[3] &= ~settings
        else:
            tc_attrs[3] |= settings
        hw.termios_tcsetattr(self._out_fd, hw.termios_TCSANOW, tc_attrs)


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


    @property
    def cursor(self):

        return self._window.cursor


    def resize(self):

        self._window.resize()


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


    def render(self, full=False, cursor_only=False, do_cursor=False):

        data = self._window_render(full=full, encoding=self._encoding,
                                   cursor_only=cursor_only, do_cursor=do_cursor)
        self._os_write_out_fd(data)


# ----------------------------------------------------------------------------
