# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import heapq

from . import common
from . log import log
from . import scheduler
from . state import tasks, state



def clear(task):

    state.terminal.clear()
    tasks.running.append(task)



def print(task, *args):

    state.terminal.print(*args)
    tasks.running.append(task)



def print_at(task, *args):

    state.terminal.print_at(*args)
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



def run_task(task, child_task):

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
        tasks.responses[task] = (child, return_value)
        del tasks.parent[child]
        tasks.children[task].remove(child)
        common.clear_tasks_children(task)
        tasks.running.append(task)
        tasks.terminated.remove((child, return_value))
        common.clear_tasks_requests_responses(child)
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

    common.clear_tasks_requests_responses(child_task)
    if keep_running:
        tasks.terminated.append((child_task, ('stopped-by', task)))
        tasks.running.append(task)
        log.info('%r stopped by %r', child_task, task)
    else:
        log.info('%r stopped from parent %r stop', child_task, task)



_SEPARATOR = '-' * 60

def dump_state(task):

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

    def _task_lines(task, level=0):
        indent = ' ' * 4 * level
        status = _task_status(task)
        log.critical(f'{status} {indent}{task}')
        if task in tasks.children:
            for child in tasks.children[task]:
                _task_lines(child, level+1)

    log.critical(_SEPARATOR)
    _task_lines(tasks.top_task)
    log.critical(_SEPARATOR)
    log.critical('tasks=%r, state=%r', tasks, state)
    log.critical(_SEPARATOR)

    if task is not None:
        tasks.running.append(task)


# ----------------------------------------------------------------------------
