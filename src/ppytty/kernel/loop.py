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
        try:
            success, result = loop()
            while post_prompt:
                _ = _read_keyboard(prompt=post_prompt)
        except _ForcedStop as e:
            success, result = None, e

    return success, result



def loop(once=False):

    while (state.runnable_tasks or state.tasks_waiting_child or state.tasks_waiting_inbox or
           state.tasks_waiting_key or state.tasks_waiting_time or state.completed_tasks):
        state.now = hw.time_monotonic()
        if not state.runnable_tasks:
            process_tasks_waiting_key()
            process_tasks_waiting_time()
        else:
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
            log.error('%r trap %r execution failed: %r', task, trap, e)
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



def process_tasks_waiting_key(keyboard_byte=None):

    if keyboard_byte is None:
        keyboard_byte = _read_keyboard(prompt='?')

    if keyboard_byte and state.tasks_waiting_key:
        while state.tasks_waiting_key_hq:
            _, _, key_waiter = heapq.heappop(state.tasks_waiting_key_hq)
            if key_waiter in state.tasks_waiting_key:
                state.tasks_waiting_key.remove(key_waiter)
                state.cleanup_tasks_waiting_key_hq()
                state.trap_will_return(key_waiter, keyboard_byte)
                state.runnable_tasks.append(key_waiter)
                log.info('%r getting key %r', key_waiter, keyboard_byte)
                break



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

def _read_keyboard(prompt=None):

    quit_in_progress = False

    if state.tasks_waiting_time:
        timeout = max(state.tasks_waiting_time_hq[0][0] - state.now, 0)
    else:
        timeout = None
    save_timeout = timeout
    while True:
        actual_prompt = 'QUIT?' if quit_in_progress else prompt
        with _prompt_context(actual_prompt):
            fds, _, _ = hw.select_select(state.in_fds, _NO_FDS, _NO_FDS, timeout)
        if state.user_in_fd in fds:
            keyboard_byte = hw.os_read(state.user_in_fd, 1)
            if keyboard_byte == b'q':
                if quit_in_progress:
                    raise _ForcedStop()
                else:
                    quit_in_progress = True
                    timeout = None
                continue
            elif quit_in_progress:
                quit_in_progress = False
                timeout = save_timeout
                continue
            elif keyboard_byte == b'D':
                trap_handlers[Trap.STATE_DUMP](None)
                continue
            return keyboard_byte
        elif not quit_in_progress:
            break


# ----------------------------------------------------------------------------
