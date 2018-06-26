# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
Hardware

This module brings together all the system I/O calls used by the kernel with
the purpuse of supporting kernel testing via monkey-patching any/all of its
attributes.
"""

import os as _os
import select as _select
import sys as _sys
import termios as _termios
import time as _time


os_read = _os.read
os_write = _os.write
os_ttyname = _os.ttyname

select_select = _select.select

sys_stdin = _sys.stdin
sys_stdout = _sys.stdout

termios_tcgetattr = _termios.tcgetattr
termios_tcsetattr = _termios.tcsetattr
termios_ICANON = _termios.ICANON
termios_ECHO = _termios.ECHO
termios_ISIG = _termios.ISIG
termios_TCSANOW = _termios.TCSANOW

time_monotonic = _time.monotonic


# ----------------------------------------------------------------------------