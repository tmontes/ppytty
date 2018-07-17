# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import fcntl
import os
import struct
import subprocess
import termios



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

        ws = struct.pack('HHHH', self._window.height, self._window.width, 0, 0)
        fcntl.ioctl(self._pty_master, termios.TIOCSWINSZ, ws)


    @staticmethod
    def _set_stdin_as_controlling_terminal():

        fcntl.fcntl(0, termios.TIOCSCTTY, 0)


    def __repr__(self):

        # TODO: improve this
        return f'<Process PID={self.pid}>'


    @property
    def pid(self):

        return self._process.pid


    def wrap_up(self, status):

        # Keep exit code and signal for interested parties.
        self._exit_code = status >> 8
        self._exit_signal = status & 0xff

        # Someone else did the wait system call for us on the process.
        # Calling .wait() on the Popen object ensures the proper internal clean
        # up, avoiding a misleading ResourceWarning.
        self._process.wait()

        # Process gone, close the PTY.
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
