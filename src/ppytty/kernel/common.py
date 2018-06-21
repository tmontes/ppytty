# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import tasks, state



def clear_tasks_children(task):

    if not tasks.children[task]:
        del tasks.children[task]



def clear_tasks_traps(task):

    for target in (tasks.trap_calls, tasks.trap_results):
        if task in target:
            del target[task]



def clear_tasks_waiting_on_time_hq():

    if not tasks.waiting_on_time:
        tasks.waiting_on_time_hq.clear()



# TODO: Do we need a "clear_tasks_waiting_on_key_hq"? Probably.



def destroy_task_windows(task):

    need_rerender = bool(tasks.windows[task])

    for window in tasks.windows[task]:
        state.all_windows.remove(window)
    del tasks.windows[task]

    if need_rerender:
        rerender_all_windows()



def rerender_all_windows():

    state.terminal.clear()

    for w in state.all_windows:
        data = w.render(full=True)
        state.terminal.feed(data)

    state.terminal.render()


# ----------------------------------------------------------------------------
