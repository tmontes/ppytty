# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import sys


class Terminal(object):

    def __init__(self):
        self._fail_if_not_tty(sys.stdin)
        self._fail_if_not_tty(sys.stdout)

    def _fail_if_not_tty(self, stream):
        if not stream.isatty():
            raise RuntimeError(f'{stream.name} must be a TTY')

    def _setup(self):
        print('setup the terminal')
        # TODO: disable canonical mode
        # TODO: disable echo
        # TODO: hide cursor
        # TODO: get terminal width and height
        # TODO: activate "alternative" screen?

    def _cleanup(self):
        print('cleanup the terminal')
        # TODO: undo all terminal settings in self._setup()

    def __enter__(self):
        self._setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup()
        # TODO: Handle exceptions or let them through?

    def print(self, *args, **kwargs):
        print('TERM:', *args, **kwargs)

# ----------------------------------------------------------------------------
