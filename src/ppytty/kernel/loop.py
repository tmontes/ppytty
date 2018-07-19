# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import contextlib
import heapq
import inspect
import logging
import os
import signal

from . import hw
from . import exceptions
from . traps import handlers as trap_handlers, Trap
from . import common
from . state import state
from . terminal import Terminal



log = logging.getLogger(__name__)



class _ForcedStop(Exception):

    pass



def run(task, post_prompt=None):

    with Terminal() as t:
        state.prepare_to_run(task, t)
        track_child_process_termination()
        try:
            success, result = loop()
            while post_prompt:
                process_lowlevel_io(prompt=post_prompt)
        except _ForcedStop as e:
            success, result = None, e

    return success, result



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
            orig_callback()
            fd = process.pty_master_fd
            if not pending_read(fd):
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



def loop(once=False):

    while (state.runnable_tasks or state.tasks_waiting_child or state.tasks_waiting_inbox or
           state.tasks_waiting_key or state.tasks_waiting_time or state.completed_tasks or
           state.tasks_waiting_processes):
        state.now = hw.time_monotonic()
        process_lowlevel_io()
        process_tasks_waiting_key()
        process_tasks_waiting_time()
        if state.runnable_tasks:
            task = state.runnable_tasks.popleft()
            try:
                trap = run_task_until_trap(task)
            except StopIteration as return_:
                log.info('%r completed with %r', task, return_.value)
                process_task_completion(task, success=True, result=return_.value)
            except Exception as e:
                log.warning('%r crashed with %r', task, e)
                process_task_completion(task, success=False, result=e)
            else:
                process_task_trap(task, trap)
        if once:
            break

    return state.top_task_success, state.top_task_result



def process_task_trap(task, trap):

    log.debug('%r trap: %r', task, trap)
    state.trap_call[task] = trap
    trap_id, *trap_args = trap
    try:
        trap_handler = trap_handlers[trap_id]
    except KeyError:
        log.error('%r trap does not exist: %r', task, trap)
        state.trap_will_throw(task, exceptions.TrapDoesNotExist(trap_id))
        state.runnable_tasks.append(task)
    else:
        try:
            trap_handler(task, *trap_args)
        except Exception as e:
            if isinstance(e, TypeError):
                # TypeError may result from non-matching trap_args
                handler_signature = inspect.signature(trap_handler)
                try:
                    handler_signature.bind(*trap_args)
                except TypeError as te:
                    # trap_args does not match trap_handle signature
                    log.error('%r bad trap args: %r', task, trap)
                    state.trap_will_throw(task, exceptions.TrapArgCountWrong(*te.args))
                    state.runnable_tasks.append(task)
                    return
            log.error('%r trap %r execution failed', task, trap, exc_info=True)
            # TODO: trap handler execution failed: inconsistent state? panic?



def run_task_until_trap(task):

    prev_trap_call = state.trap_call.get(task)
    prev_trap_success = state.trap_success.get(task)
    prev_trap_result = state.trap_result.get(task)
    if prev_trap_call is not None:
        log.debug('%r trap %r result: %r', task, prev_trap_call, prev_trap_result)
    elif prev_trap_result is not None:
        log.error('%r no trap result: %r', task, prev_trap_result)
    else:
        log.debug('%r running', task)
    try:
        run_task = task.throw if prev_trap_success is False else task.send
        return run_task(prev_trap_result)
    finally:
        state.clear_trap_info(task)



def process_tasks_waiting_key():

    while state.terminal.input_buffer and state.tasks_waiting_key:
        keyboard_bytes = state.terminal.input_buffer.popleft()
        key_waiter = state.tasks_waiting_key.popleft()
        state.trap_will_return(key_waiter, keyboard_bytes)
        state.runnable_tasks.append(key_waiter)
        log.info('%r getting key %r', key_waiter, keyboard_bytes)



def process_tasks_waiting_time():

    if state.tasks_waiting_time:
        while state.tasks_waiting_time_hq and state.tasks_waiting_time_hq[0][0] <= state.now:
            _, _, time_waiter = heapq.heappop(state.tasks_waiting_time_hq)
            if time_waiter in state.tasks_waiting_time:
                state.tasks_waiting_time.remove(time_waiter)
                state.cleanup_tasks_waiting_time_hq()
                state.runnable_tasks.append(time_waiter)
                log.info('%r waking up', time_waiter)



_NOT_THERE = object()

def process_task_completion(task, success, result):

    candidate_parent = state.parent_task.get(task)
    if not candidate_parent and task is not state.top_task:
        log.error('%r completed with no parent', task)
    if candidate_parent in state.tasks_waiting_child:
        user_space_task = state.user_space_tasks[task]
        state.trap_will_return(candidate_parent, (user_space_task, success, result))
        state.clear_kernel_task_mapping(task)
        del state.parent_task[task]
        state.child_tasks[candidate_parent].remove(task)
        state.cleanup_child_tasks(candidate_parent)
        state.tasks_waiting_child.remove(candidate_parent)
        state.runnable_tasks.append(candidate_parent)
    elif task is not state.top_task and task in state.parent_task:
        state.completed_tasks[task] = (success, result)
    elif task is state.top_task:
        state.top_task_success = success
        state.top_task_result = result
    if success is False:
        # Prevent kernel hang by cleaning up completed child results, if any.
        # We no longer have a parent to wait for them.
        for child_task in state.child_tasks[task]:
            child_result = state.completed_tasks.pop(child_task, _NOT_THERE)
            if child_result is not _NOT_THERE:
                log.warning('%r dropping completed child result: %r', task, child_result)
    state.clear_task_parenthood(task)
    state.clear_trap_info(task)
    common.destroy_task_windows(task)
    if task in state.task_processes:
        log.warning('%r did not wait for spawned processes: %r', task, state.task_processes[task])



def _prompt_context(prompt):

    @contextlib.contextmanager
    def _prompt(prompt):
        col = state.terminal.width - len(prompt)
        row = state.terminal.height - 1
        state.terminal.direct_print(prompt, col, row, save_location=True)
        yield
        state.terminal.direct_print(' '*len(prompt), col, row, save_location=True)

    @contextlib.contextmanager
    def _no_prompt():
        yield

    return _prompt(prompt) if prompt else _no_prompt()



_NO_FDS = []

_KEY_GRAB = b'\x06'
_KEY_STOP = b'.'
_KEY_DUMP = b'd'
_KEY_FOCUS = b'f'

def process_lowlevel_io(prompt=None):

    def forward_keybard_input(process, keyboard_bytes):
        if process:
            hw.os_write(process.pty_master_fd, keyboard_bytes)
        else:
            state.terminal.input_buffer.append(keyboard_bytes)

    def visual_focus_change():
        process = state.focused_process
        window = state.focused_window
        t_cursor = state.terminal.cursor
        if process:
            w_cursor = window.cursor
            t_cursor.hidden = w_cursor.hidden
            t_cursor.x = window.left + w_cursor.x
            t_cursor.y = window.top + w_cursor.y
        else:
            t_cursor.hidden = True
        state.terminal.render(cursor_only=True)
        log.info('input focus on %r/%r', process, window)


    grab_terminal_input = False
    focused_process = state.focused_process

    if state.runnable_tasks:
        timeout = 0
    elif state.tasks_waiting_time:
        timeout = max(state.tasks_waiting_time_hq[0][0] - state.now, 0)
    else:
        timeout = None
    save_timeout = timeout
    while True:
        actual_prompt = '[GRAB]' if grab_terminal_input else prompt
        with _prompt_context(actual_prompt):
            fds, _, _ = hw.select_select(state.in_fds, _NO_FDS, _NO_FDS, timeout)
        for fd in fds:
            in_fd_callable = state.in_fds[fd]
            if in_fd_callable is None:
                keyboard_bytes = hw.os_read(fd, 8)
                if grab_terminal_input:
                    if keyboard_bytes == _KEY_STOP:
                        raise _ForcedStop()
                    elif keyboard_bytes == _KEY_DUMP:
                        trap_handlers[Trap.STATE_DUMP](None)
                    elif keyboard_bytes == _KEY_FOCUS:
                        state.next_window_process_focus()
                        visual_focus_change()
                    elif keyboard_bytes == _KEY_GRAB:
                        # _KEY_GRAB as non-grabbed input
                        forward_keybard_input(focused_process, keyboard_bytes)
                    grab_terminal_input = False
                    timeout = save_timeout
                else:
                    if keyboard_bytes == _KEY_GRAB:
                        grab_terminal_input = True
                        timeout = None
                    else:
                        forward_keybard_input(focused_process, keyboard_bytes)
            else:
                in_fd_callable()
        while state.close_fd_callables:
            state.close_fd_callables.pop()()
        if not grab_terminal_input:
            break


# ----------------------------------------------------------------------------
