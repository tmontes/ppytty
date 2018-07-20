# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
Signals

This module brings 
"""

import logging
import os
import signal

from . import hw
from . state import state



log = logging.getLogger(__name__)



_NO_FDS = []

def track_child_process_termination():

    # TODO: These should be closed, on exiting!
    read_fd, write_fd = os.pipe()

    def wakeup_lowlevel_io():
        os.write(write_fd, b'!')

    def consume_wakeup_byte():
        os.read(read_fd, 1)

    def signal_handler(_signal, _frame):
        pid, status = os.wait()
        log.info('SIGCHLD from pid=%r, status=%r', pid, status)
        try:
            process = state.all_processes[pid]
        except KeyError:
            log.error('SIGCHLD child process not found')
        else:
            try:
                task = state.process_task[process]
            except KeyError:
                log.error('SIGCHLD task not found')
            else:
                handle_process_termination(task, process, status)


    def pending_read(fd):

        return hw.select_select([fd], _NO_FDS, _NO_FDS, 0)[0]

    def handle_process_termination(task, process, status):

        process.store_exit_status(status)
        fd = process.pty_master_fd
        if pending_read(fd):
            orig_callback = state.in_fds[fd]
            new_callback = read_and_wrap_up(orig_callback, task, process)
            state.track_input_fd(fd, new_callback)
        else:
            wrap_up(task, process)
            wakeup_lowlevel_io()

    def read_and_wrap_up(orig_callback, task, process):

        def new_callback():
            # orig_callback: `updater` function on `process_spawn` trap code.
            data = orig_callback()
            fd = process.pty_master_fd
            if not data or not pending_read(fd):
                wrap_up(task, process)

        return new_callback

    def wrap_up(task, process):

        state.discard_input_fd(process.pty_master_fd)
        state.close_fd_callables.append(process.close_pty)
        state.cleanup_focusable_window_process(process=process)
        if task in state.tasks_waiting_processes:
            state.tasks_waiting_processes.remove(task)
            state.cleanup_task_process(task, process)
            state.trap_will_return(task, process)
            state.runnable_tasks.append(task)
        else:
            state.completed_processes[task].append(process)

    state.track_input_fd(read_fd, consume_wakeup_byte)
    signal.signal(signal.SIGCHLD, signal_handler)




# ----------------------------------------------------------------------------