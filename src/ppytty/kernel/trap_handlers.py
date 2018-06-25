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
from . state import tasks, state, io_fds
from . window import Window



log = logging.getLogger(__name__)



def direct_clear(task):

    state.terminal.direct_clear()
    tasks.running.append(task)



def direct_print(task, *args):

    state.terminal.direct_print(*args)
    tasks.running.append(task)



def window_create(task, left, top, width, height, bg=None):

    try:
        w = Window(left, top, width, height, bg)
    except Exception as e:
        log.error('%r window create failed: %s', task, e)
        log.debug('%r traceback', task, exc_info=True)
        w = None
    else:
        tasks.windows[task].append(w)
        state.all_windows.append(w)

    tasks.trap_results[task] = w
    tasks.running.append(task)



def window_destroy(task, window):

    if not window in tasks.windows[task]:
        raise RuntimeError('cannot destroy non-owned windows')

    tasks.windows[task].remove(window)
    state.all_windows.remove(window)

    # One window is gone: need to re-render everything to account for it.
    # Possible optimizations:
    # - If completely within another window, just rerender that window.
    # - Just clear needed terminal lines and rerender overlapping windows.
    common.rerender_all_windows()

    tasks.running.append(task)



def window_render(task, window, full=False):

    if not window in tasks.windows[task]:
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

    tasks.running.append(task)



def sleep(task, seconds):

    wake_at = state.now + seconds
    tasks.waiting_on_time.append(task)
    heapq.heappush(tasks.waiting_on_time_hq, (wake_at, id(task), task))



def read_key(task, priority):

    tasks.waiting_on_key.append(task)
    heapq.heappush(tasks.waiting_on_key_hq, (priority, id(task), task))



def put_key(task, pushed_back_key):

    scheduler.process_tasks_waiting_on_key(pushed_back_key)
    tasks.running.append(task)



def task_spawn(task, child_task):

    tasks.parent[child_task] = task
    tasks.children[task].append(child_task)
    tasks.running.append(child_task)
    tasks.running.append(task)



def wait_task(task):

    child = None
    for candidate, return_value in tasks.terminated:
        if tasks.parent[candidate] is task:
            child = candidate
            break
    if child is not None:
        tasks.trap_results[task] = (child, return_value)
        del tasks.parent[child]
        tasks.children[task].remove(child)
        common.clear_tasks_children(task)
        tasks.running.append(task)
        tasks.terminated.remove((child, return_value))
        common.clear_tasks_traps(child)
    else:
        tasks.waiting_on_child.append(task)



def stop_task(task, child_task, keep_running=True):

    if tasks.parent[child_task] is not task:
        raise RuntimeError('cannot kill non-child tasks')

    if child_task in tasks.children:
        for grand_child_task in tasks.children[child_task]:
            stop_task(child_task, grand_child_task, keep_running=False)
            del tasks.parent[grand_child_task]
        del tasks.children[child_task]

    if child_task in tasks.running:
        tasks.running.remove(child_task)
    elif child_task in tasks.waiting_on_child:
        tasks.waiting_on_child.remove(child_task)
    elif child_task in tasks.waiting_on_key:
        tasks.waiting_on_key.remove(child_task)
    elif child_task in tasks.waiting_on_time:
        tasks.waiting_on_time.remove(child_task)
        common.clear_tasks_waiting_on_time_hq()
    else:
        terminated = [t for (t, _) in tasks.terminated if t is child_task]
        if terminated:
            log.error('%r will not stop terminated task %r', task, child_task)
        return

    common.clear_tasks_traps(child_task)
    common.destroy_task_windows(child_task)
    if keep_running:
        tasks.terminated.append((child_task, ('stopped-by', task)))
        tasks.running.append(task)
        log.info('%r stopped by %r', child_task, task)
    else:
        log.info('%r stopped from parent %r stop', child_task, task)



_SEPARATOR = '-' * 60

def dump_state(task, tag=''):

    def _task_status(task):
        if task in tasks.running:
            return 'RR'
        if task in tasks.waiting_on_child:
            return 'WC'
        if task in tasks.waiting_on_key:
            return 'WK'
        if task in tasks.waiting_on_time:
            return 'WT'
        if task in (t for (t, _) in tasks.terminated):
            return 'TT'
        return '??'

    def _log_task_lines(task, level=0):
        indent = ' ' * 4 * level
        status = _task_status(task)
        log.critical(f'{status} {indent}{task}')
        if task in tasks.children:
            for child in tasks.children[task]:
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
    _log_task_lines(tasks.top_task)
    log.critical(f'-[ {tag_string}DUMP STATE | DATA STRUCTURES ]'.ljust(60, '-'))
    _log_object_vars('tasks', tasks)
    _log_object_vars('state', state)
    _log_object_vars('io_fds', io_fds)
    log.critical(f'-[ {tag_string}DUMP STATE | DONE ]'.ljust(60, '-'))

    if task is not None:
        tasks.running.append(task)


# ----------------------------------------------------------------------------
