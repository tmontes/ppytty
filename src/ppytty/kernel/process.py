# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import fcntl
import logging
import os
import signal
import struct
import subprocess
import termios



log = logging.getLogger(__name__)



class Process(object):

    def __init__(self, window, args):

        self._window = window
        self._args = args

        master, slave = os.openpty()
        self._pty_master = master
        self._pty_slave = slave
        self._set_pty_window_size()

        # TODO: Currently passing environment copy to child process. Change?
        self._process = subprocess.Popen(
            args, bufsize=0, stdin=slave, stdout=slave, stderr=slave,
            start_new_session=True,
            preexec_fn=self._set_stdin_as_controlling_terminal
        )

        # Will be assigned when the process terminates
        self._exit_code = None
        self._exit_signal = None


    def _set_pty_window_size(self):

        try:
            ws = struct.pack('HHHH', self._window.height, self._window.width, 0, 0)
            fcntl.ioctl(self._pty_master, termios.TIOCSWINSZ, ws)
        except struct.error as e:
            log.warning('%r: invalid geometry for PTY w=%r h=%r: %r', self,
                        self._window.width, self._window.height, e)
        except OSError as e:
            log.warning('%r: setting PTY geometry failed: %r', self, e)


    @staticmethod
    def _set_stdin_as_controlling_terminal():

        try:
            fcntl.ioctl(0, termios.TIOCSCTTY, 0)
        except OSError as e:
            # This runs in the spawned child process, we can't log errors.
            # The best we can do is output them to the child's STDERR.
            msg = f'Failed setting STDIN as controlling terminal: {e!r}'
            os.write(2, msg.encode('ascii', errors='xmlcharrefreplace'))

    def __repr__(self):

        # TODO: improve this
        return f'<Process PID={self.pid}>'


    @property
    def pid(self):

        return self._process.pid


    def resize_pty(self, _window):

        self._set_pty_window_size()
        self._process.send_signal(signal.SIGWINCH)


    def store_exit_status(self, status):

        # Keep exit code and signal for interested parties.
        self._exit_code = status >> 8
        self._exit_signal = status & 0xff

        # Someone else did the wait system call for us on the process.
        # Calling .wait() on the Popen object ensures the proper internal clean
        # up, avoiding a misleading ResourceWarning.
        self._process.wait()


    def close_pty(self):

        os.close(self._pty_master)
        os.close(self._pty_slave)


    @property
    def pty_master_fd(self):

        return self._pty_master


    @property
    def exit_code(self):

        return self._exit_code


    @property
    def exit_signal(self):

        return self._exit_signal


    def signal(self, signal):

        return self._process.send_signal(signal)


    def terminate(self):

        return self._process.terminate()


    def kill(self):

        return self._process.kill()


# ----------------------------------------------------------------------------
