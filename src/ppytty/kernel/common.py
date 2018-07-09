# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import state



def kernel_task(user_task):

    try:
        kernel_task = state.kernel_space_tasks[user_task]
    except KeyError:
        kernel_task = user_task() if callable(user_task) else user_task
    return kernel_task



def clear_tasks_children(task):

    if not state.child_tasks[task]:
        del state.child_tasks[task]



def clear_task_parenthood(parent_task):

    for child_task in state.child_tasks[parent_task]:
        del state.parent_task[child_task]



def clear_tasks_waiting_time_hq():

    if not state.tasks_waiting_time:
        state.tasks_waiting_time_hq.clear()



# TODO: Do we need a "clear_tasks_waiting_key_hq"? Probably.



def destroy_task_windows(task):

    need_rerender = bool(state.task_windows[task])

    for window in state.task_windows[task]:
        state.all_windows.remove(window)
    del state.task_windows[task]

    if need_rerender:
        rerender_all_windows()



def rerender_all_windows():

    state.terminal.clear()

    for w in state.all_windows:
        data = w.render(full=True)
        state.terminal.feed(data)

    state.terminal.render()


# ----------------------------------------------------------------------------
