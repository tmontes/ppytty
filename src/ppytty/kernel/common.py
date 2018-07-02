# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import state



def kernel_task(user_task):

    kernel_task = user_task() if callable(user_task) else user_task
    state.user_space_tasks[kernel_task] = user_task
    state.kernel_space_tasks[user_task] = kernel_task
    return kernel_task



def clear_user_kernel_task_mapping(kernel_task, user_task):

    del state.user_space_tasks[kernel_task]
    del state.kernel_space_tasks[user_task]



def clear_tasks_children(task):

    if not state.child_tasks[task]:
        del state.child_tasks[task]



def clear_task_parenthood(parent_task):

    for child_task in state.child_tasks[parent_task]:
        del state.parent_task[child_task]



def trap_will_return(task, result):

    state.trap_success[task] = True
    state.trap_result[task] = result



def trap_will_throw(task, exception_class):

    state.trap_success[task] = False
    state.trap_result[task] = exception_class



def clear_tasks_traps(task):

    for target in (state.trap_call, state.trap_success, state.trap_result):
        if task in target:
            del target[task]



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
