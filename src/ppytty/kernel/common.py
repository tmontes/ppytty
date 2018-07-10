# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import state



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
