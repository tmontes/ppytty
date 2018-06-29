# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import collections
import heapq
import logging

from . import common
from . import scheduler
from . state import state
from . window import Window



log = logging.getLogger(__name__)



def direct_clear(task):

    state.terminal.direct_clear()
    state.runnable_tasks.append(task)



def direct_print(task, *args):

    state.terminal.direct_print(*args)
    state.runnable_tasks.append(task)



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

    common.trap_will_return(task, w)
    state.runnable_tasks.append(task)



def window_destroy(task, window):

    if not window in state.task_windows[task]:
        raise RuntimeError('cannot destroy non-owned windows')

    state.task_windows[task].remove(window)
    state.all_windows.remove(window)

    # One window is gone: need to re-render everything to account for it.
    # Possible optimizations:
    # - If completely within another window, just rerender that window.
    # - Just clear needed terminal lines and rerender overlapping windows.
    common.rerender_all_windows()

    state.runnable_tasks.append(task)



def window_render(task, window, full=False):

    if not window in state.task_windows[task]:
        raise RuntimeError('cannot render non-owned windows')

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



def sleep(task, seconds):

    wake_at = state.now + seconds
    state.tasks_waiting_time.append(task)
    heapq.heappush(state.tasks_waiting_time_hq, (wake_at, id(task), task))



def read_key(task, priority):

    state.tasks_waiting_key.append(task)
    heapq.heappush(state.tasks_waiting_key_hq, (priority, id(task), task))



def put_key(task, pushed_back_key):

    scheduler.process_tasks_waiting_key(pushed_back_key)
    state.runnable_tasks.append(task)



def task_spawn(task, child_task):

    child_task = common.runnable_task(child_task)
    state.parent_task[child_task] = task
    state.child_tasks[task].append(child_task)
    state.runnable_tasks.append(child_task)
    state.runnable_tasks.append(task)



def task_wait(task):

    child = None
    for candidate in state.completed_tasks:
        if state.parent_task[candidate] is task:
            child = candidate
            success, result = state.completed_tasks[child]
            break
    if child is not None:
        common.trap_will_return(task, (child, success, result))
        del state.parent_task[child]
        state.child_tasks[task].remove(child)
        common.clear_tasks_children(task)
        state.runnable_tasks.append(task)
        del state.completed_tasks[child]
        common.clear_tasks_traps(child)
    else:
        state.tasks_waiting_child.append(task)



def task_destroy(task, child_task, keep_running=True):

    if state.parent_task[child_task] is not task:
        raise RuntimeError('cannot kill non-child tasks')

    if child_task in state.child_tasks:
        for grand_child_task in state.child_tasks[child_task]:
            task_destroy(child_task, grand_child_task, keep_running=False)
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
        common.clear_tasks_waiting_time_hq()
    elif child_task in state.completed_tasks:
        log.error('%r will not stop completed task %r', task, child_task)
    else:
        return

    common.clear_tasks_traps(child_task)
    common.destroy_task_windows(child_task)
    if keep_running:
        state.completed_tasks[child_task]  = (False, ('destroyed-by', task))
        state.runnable_tasks.append(task)
        log.info('%r destroyed by %r', child_task, task)
    else:
        log.info('%r destroyed from parent %r destroy', child_task, task)



def message_send(task, to_task, message):

    if to_task is None:
        to_task = state.parent_task.get(task)
        if to_task is None:
            log.warning('%r no parent task for message send', task)
            # TODO: throw an exception into the calling task?
            return

    if to_task in state.tasks_waiting_inbox:
        state.tasks_waiting_inbox.remove(to_task)
        common.trap_will_return(to_task, (task, message))
        state.runnable_tasks.append(to_task)
    else:
        state.task_inbox[to_task].append((task, message))

    state.runnable_tasks.append(task)



def message_wait(task):

    task_inbox = state.task_inbox[task]
    if task_inbox:
        sender_task, message = task_inbox.popleft()
        common.trap_will_return(task, (sender_task, message))
        state.runnable_tasks.append(task)
    else:
        state.tasks_waiting_inbox.append(task)



_SEPARATOR = '-' * 60

def state_dump(task, tag=''):

    def _task_status(task):
        if task in state.runnable_tasks:
            return 'RR'
        if task in state.tasks_waiting_child:
            return 'WC'
        if task in state.tasks_waiting_key:
            return 'WK'
        if task in state.tasks_waiting_time:
            return 'WT'
        if task in state.completed_tasks:
            return 'TT'
        return '??'

    def _log_task_lines(task, level=0):
        indent = ' ' * 4 * level
        status = _task_status(task)
        log.critical(f'{status} {indent}{task}')
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
