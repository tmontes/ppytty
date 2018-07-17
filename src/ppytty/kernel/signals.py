# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import logging
import os
import signal

from . state import state



log = logging.getLogger(__name__)



def sigchld_handler(_signal, _frame):

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
            process.exit_status = status
            state.completed_processes[task].append(process)



def install_signal_handlers():

    signal.signal(signal.SIGCHLD, sigchld_handler)
    log.info('installed SIGCHLD handler')


# ----------------------------------------------------------------------------
