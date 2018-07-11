# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import enum
import collections
import heapq
import logging

from . import exceptions
from . import common
from . import loop
from . state import state
from . window import Window



log = logging.getLogger(__name__)



# ----------------------------------------------------------------------------
# Trap idenfifiers

class Trap(enum.Enum):

    DIRECT_CLEAR = enum.auto()
    DIRECT_PRINT = enum.auto()

    WINDOW_CREATE = enum.auto()
    WINDOW_RENDER = enum.auto()
    WINDOW_DESTROY = enum.auto()

    SLEEP = enum.auto()

    KEY_READ = enum.auto()
    KEY_UNREAD = enum.auto()

    TASK_SPAWN = enum.auto()
    TASK_DESTROY = enum.auto()
    TASK_WAIT = enum.auto()

    MESSAGE_SEND = enum.auto()
    MESSAGE_WAIT = enum.auto()

    STATE_DUMP = enum.auto()



# ----------------------------------------------------------------------------
# Trap identifier to handler function mapping.


# Maps Trap identifiers to handler functions.

handlers = {}


# Decorator function that populates the handlers map.

def handler_for(trap_id):

    def decorator_function(trap_handler):

        if trap_id in handlers:
            raise ValueError(f'duplicate handler for {trap_id}')
        handlers[trap_id] = trap_handler

        return trap_handler

    return decorator_function



# ----------------------------------------------------------------------------
# Trap handlers


@handler_for(Trap.DIRECT_CLEAR)
def direct_clear(task):

    state.terminal.direct_clear()
    state.runnable_tasks.append(task)



@handler_for(Trap.DIRECT_PRINT)
def direct_print(task, *args):

    state.terminal.direct_print(*args)
    state.runnable_tasks.append(task)



@handler_for(Trap.WINDOW_CREATE)
def window_create(task, left, top, width, height, bg=None):

    try:
        w = Window(left, top, width, height, bg)
    except Exception as e:
        log.error('%r window create failed: %s', task, e)
        log.debug('%r traceback', task, exc_info=True)
        w = None
    else:
        state.task_windows[task].append(w)
        state.all_windows.append(w)

    state.trap_will_return(task, w)
    state.runnable_tasks.append(task)



@handler_for(Trap.WINDOW_DESTROY)
def window_destroy(task, window):

    if not window in state.task_windows[task]:
        state.trap_will_throw(task, exceptions.TrapException('no such window'))
        state.runnable_tasks.append(task)
        return

    state.task_windows[task].remove(window)
    state.all_windows.remove(window)

    # One window is gone: need to re-render everything to account for it.
    # Possible optimizations:
    # - If completely within another window, just rerender that window.
    # - Just clear needed terminal lines and rerender overlapping windows.
    common.rerender_all_windows()

    state.runnable_tasks.append(task)



@handler_for(Trap.WINDOW_RENDER)
def window_render(task, window, full=False):

    if not window in state.task_windows[task]:
        state.trap_will_throw(task, exceptions.TrapException('no such window'))
        state.runnable_tasks.append(task)
        return

    # Render `window` and all other windows that:
    # - Overlap with it.
    # - Are on top of it.

    try:
        window_index = state.all_windows.index(window)
    except ValueError:
        raise RuntimeError('unexpected condition: window not in all_windows')

    data = window.render(full=full)
    state.terminal.feed(data)

    for w in state.all_windows[window_index+1:]:
        if not w.overlaps(window):
            continue
        data = w.render(full=True)
        state.terminal.feed(data)

    state.terminal.render()

    state.runnable_tasks.append(task)



@handler_for(Trap.SLEEP)
def sleep(task, seconds):

    if seconds <= 0:
        state.runnable_tasks.append(task)
        return

    wake_at = state.now + seconds
    state.tasks_waiting_time.append(task)
    heapq.heappush(state.tasks_waiting_time_hq, (wake_at, id(task), task))



@handler_for(Trap.KEY_READ)
def key_read(task):

    state.tasks_waiting_key.append(task)



@handler_for(Trap.KEY_UNREAD)
def key_unread(task, pushed_back_bytes):

    if state.tasks_waiting_key:
        key_waiter = state.tasks_waiting_key.popleft()
        state.trap_will_return(key_waiter, pushed_back_bytes)
        state.runnable_tasks.append(key_waiter)
    else:
        state.terminal.input_buffer.append(pushed_back_bytes)
    state.runnable_tasks.append(task)



@handler_for(Trap.TASK_SPAWN)
def task_spawn(task, user_child_task):

    child_task = state.get_mapped_kernel_task(user_child_task)
    state.parent_task[child_task] = task
    state.child_tasks[task].append(child_task)
    state.runnable_tasks.append(child_task)
    state.runnable_tasks.append(task)



@handler_for(Trap.TASK_WAIT)
def task_wait(task):

    child = None
    for candidate in state.completed_tasks:
        if state.parent_task[candidate] is task:
            child = candidate
            success, result = state.completed_tasks[child]
            break
    if child is not None:
        user_space_task = state.user_space_tasks[child]
        state.trap_will_return(task, (user_space_task, success, result))
        state.clear_kernel_task_mapping(child)
        del state.parent_task[child]
        state.child_tasks[task].remove(child)
        state.cleanup_child_tasks(task)
        state.runnable_tasks.append(task)
        del state.completed_tasks[child]
        state.clear_trap_info(child)
    else:
        state.tasks_waiting_child.append(task)



@handler_for(Trap.TASK_DESTROY)
def task_destroy(task, user_child_task, keep_running=True):

    try:
        child_task = state.kernel_space_tasks[user_child_task]
    except KeyError:
        state.trap_will_throw(task, exceptions.TrapException('no such task'))
        state.runnable_tasks.append(task)
        return

    if state.parent_task[child_task] is not task:
        exc = exceptions.TrapException('cannot destroy non-child tasks')
        state.trap_will_throw(task, exc)
        state.runnable_tasks.append(task)
        return

    if child_task in state.child_tasks:
        for grand_child_task in state.child_tasks[child_task]:
            user_grand_child_task = state.user_space_tasks[grand_child_task]
            task_destroy(child_task, user_grand_child_task, keep_running=False)
            del state.parent_task[grand_child_task]
        del state.child_tasks[child_task]

    if child_task in state.runnable_tasks:
        state.runnable_tasks.remove(child_task)
    elif child_task in state.tasks_waiting_child:
        state.tasks_waiting_child.remove(child_task)
    elif child_task in state.tasks_waiting_key:
        state.tasks_waiting_key.remove(child_task)
    elif child_task in state.tasks_waiting_time:
        state.tasks_waiting_time.remove(child_task)
        state.cleanup_tasks_waiting_time_hq()
    elif child_task in state.tasks_waiting_inbox:
        state.tasks_waiting_inbox.remove(child_task)
    elif child_task in state.completed_tasks:
        del state.completed_tasks[child_task]
    else:
        # TODO: Should not happen. Should the kernel panic?
        log.error('%r cannot destroy non-found task %r', task, child_task)
        return

    state.clear_trap_info(child_task)
    common.destroy_task_windows(child_task)
    if keep_running:
        state.completed_tasks[child_task]  = (False, exceptions.TrapDestroyed(task))
        state.runnable_tasks.append(task)
        log.info('%r destroyed by %r', child_task, task)
    else:
        log.info('%r destroyed from parent %r destroy', child_task, task)



@handler_for(Trap.MESSAGE_SEND)
def message_send(task, to_user_task, message):

    if to_user_task is None:
        try:
            to_task = state.parent_task[task]
        except KeyError:
            exc = exceptions.TrapException('no parent task for message send')
            state.trap_will_throw(task, exc)
            state.runnable_tasks.append(task)
            return
    else:
        to_task = state.kernel_space_tasks[to_user_task]

    if to_task in state.tasks_waiting_inbox:
        state.tasks_waiting_inbox.remove(to_task)
        user_space_task = state.user_space_tasks[task]
        state.trap_will_return(to_task, (user_space_task, message))
        state.runnable_tasks.append(to_task)
    else:
        state.task_inbox[to_task].append((task, message))

    state.runnable_tasks.append(task)



@handler_for(Trap.MESSAGE_WAIT)
def message_wait(task):

    task_inbox = state.task_inbox[task]
    if task_inbox:
        sender_task, message = task_inbox.popleft()
        user_space_task = state.user_space_tasks[sender_task]
        state.trap_will_return(task, (user_space_task, message))
        state.runnable_tasks.append(task)
    else:
        state.tasks_waiting_inbox.append(task)



_SEPARATOR = '-' * 60

@handler_for(Trap.STATE_DUMP)
def state_dump(task, tag=''):

    def _task_status(task):
        if task in state.runnable_tasks:
            return 'RN'
        if task in state.tasks_waiting_child:
            return 'WC'
        if task in state.tasks_waiting_inbox:
            return 'WM'
        if task in state.tasks_waiting_key:
            return 'WK'
        if task in state.tasks_waiting_time:
            return 'WT'
        if task in state.completed_tasks:
            return 'CC'
        return 'RR'

    def _log_task_lines(task, level=0):
        indent = ' ' * 4 * level
        status = _task_status(task)
        user_space_task = state.user_space_tasks[task]
        log.critical(f'{status} {indent}{user_space_task}')
        if task in state.child_tasks:
            for child in state.child_tasks[task]:
                _log_task_lines(child, level+1)

    def _log_object_vars(name, obj):
        for k, v in vars(obj).items():
            if k.startswith('_') or callable(getattr(obj, k, None)):
                continue
            if isinstance(v, collections.defaultdict):
                v = dict(v)
            log.critical('%s.%s=%r', name, k, v)

    tag_string = f'{tag} | ' if tag else ''

    log.critical(f'-[ {tag_string}DUMP STATE | TASK HIERARCHY ]'.ljust(60, '-'))
    _log_task_lines(state.top_task)
    log.critical(f'-[ {tag_string}DUMP STATE | DATA STRUCTURES ]'.ljust(60, '-'))
    _log_object_vars('state', state)
    log.critical(f'-[ {tag_string}DUMP STATE | DONE ]'.ljust(60, '-'))

    if task is not None:
        state.runnable_tasks.append(task)


# ----------------------------------------------------------------------------
