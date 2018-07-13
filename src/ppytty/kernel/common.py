# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import state



def render_window_to_terminal(window, full):

    data = window.render(full=full)
    state.terminal.feed(data)



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
        render_window_to_terminal(w, full=True)

    state.terminal.render()


# ----------------------------------------------------------------------------
