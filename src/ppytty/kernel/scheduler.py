# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import contextlib
import heapq
import logging

from . import hw
from . import trap_handlers
from . import common
from . state import tasks, io_fds, state
from . terminal import Terminal



log = logging.getLogger(__name__)



class _SchedulerStop(Exception):

    pass



def run(task, post_prompt=None):

    with Terminal() as t:
        state.terminal = t
        io_fds.set_user_io(t.in_fd, t.out_fd)
        try:
            success, result = scheduler(task)
            while post_prompt:
                _ = _read_keyboard(prompt=post_prompt)
        except _SchedulerStop as e:
            success, result = None, e

    return success, result



def scheduler(top_task):

    top_task = common.runnable_task(top_task)
    tasks.top_task = top_task
    tasks.runnable.append(top_task)

    while (tasks.runnable or tasks.waiting_on_child or tasks.waiting_on_key or
           tasks.waiting_on_time or tasks.terminated):
        state.now = hw.time_monotonic()
        if not tasks.runnable:
            process_tasks_waiting_on_key()
            process_tasks_waiting_on_time()
            continue
        task = tasks.runnable.popleft()
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

    return tasks.top_task_success, tasks.top_task_result



def process_task_trap(task, trap):

    log.debug('%r trap: %r', task, trap)
    tasks.trap_calls[task] = trap
    trap_name, *trap_args = trap
    trap_handler_name = trap_name.replace("-", "_")
    try:
        trap_handler = getattr(trap_handlers, trap_handler_name)
    except AttributeError:
        log.error('%r invalid trap: %r', task, trap)
        # TODO: terminate task somewhat like StopIteration?
    else:
        try:
            trap_handler(task, *trap_args)
        except Exception as e:
            log.error('%r call %r execution failed: %r', task, trap, e)
            # TODO: inconsistent state? panic?



def run_task_until_trap(task):

    prev_trap_call = tasks.trap_calls.get(task)
    prev_trap_result = tasks.trap_results.get(task)
    if prev_trap_call is not None:
        log.debug('%r trap %r result: %r', task, prev_trap_call, prev_trap_result)
    elif prev_trap_result is not None:
        log.error('%r no trap result: %r', task, prev_trap_result)
    else:
        log.debug('%r running', task)
    try:
        return task.send(prev_trap_result)
    finally:
        if prev_trap_call:
            del tasks.trap_calls[task]
        if prev_trap_result:
            del tasks.trap_results[task]



def process_tasks_waiting_on_key(keyboard_byte=None):

    if keyboard_byte is None:
        keyboard_byte = _read_keyboard(prompt='?')

    if keyboard_byte and tasks.waiting_on_key:
        while tasks.waiting_on_key_hq:
            _, _, key_waiter = heapq.heappop(tasks.waiting_on_key_hq)
            if key_waiter in tasks.waiting_on_key:
                tasks.waiting_on_key.remove(key_waiter)
                tasks.trap_results[key_waiter] = keyboard_byte
                tasks.runnable.append(key_waiter)
                log.info('%r getting key %r', key_waiter, keyboard_byte)
                break



def process_tasks_waiting_on_time():

    if tasks.waiting_on_time:
        while tasks.waiting_on_time_hq and tasks.waiting_on_time_hq[0][0] < state.now:
            _, _, time_waiter = heapq.heappop(tasks.waiting_on_time_hq)
            if time_waiter in tasks.waiting_on_time:
                tasks.waiting_on_time.remove(time_waiter)
                common.clear_tasks_waiting_on_time_hq()
                tasks.runnable.append(time_waiter)
                log.info('%r waking up', time_waiter)



def process_task_completion(task, success, result):

    candidate_parent = tasks.parent.get(task)
    if not candidate_parent and task is not tasks.top_task:
        log.error('%r completed with no parent', task)
    if candidate_parent in tasks.waiting_on_child:
        tasks.trap_results[candidate_parent] = (task, success, result)
        del tasks.parent[task]
        tasks.children[candidate_parent].remove(task)
        common.clear_tasks_children(candidate_parent)
        tasks.waiting_on_child.remove(candidate_parent)
        tasks.runnable.append(candidate_parent)
    elif task is not tasks.top_task:
        tasks.terminated.append((task, success, result))
    else:
        tasks.top_task_success = success
        tasks.top_task_result = result
    common.clear_tasks_traps(task)
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

    if tasks.waiting_on_time:
        timeout = max(tasks.waiting_on_time_hq[0][0] - state.now, 0)
    else:
        timeout = None
    save_timeout = timeout
    while True:
        actual_prompt = 'QUIT?' if quit_in_progress else prompt
        with _prompt_context(actual_prompt):
            fds, _, _ = hw.select_select(io_fds.input, _NO_FDS, _NO_FDS, timeout)
        if io_fds.user_in in fds:
            keyboard_byte = hw.os_read(io_fds.user_in, 1)
            if keyboard_byte == b'q':
                if quit_in_progress:
                    raise _SchedulerStop()
                else:
                    quit_in_progress = True
                    timeout = None
                continue
            elif quit_in_progress:
                quit_in_progress = False
                timeout = save_timeout
                continue
            elif keyboard_byte == b'D':
                trap_handlers.state_dump(None)
                continue
            return keyboard_byte
        elif not quit_in_progress:
            break


# ----------------------------------------------------------------------------
