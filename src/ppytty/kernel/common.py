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



def update_terminal_cursor_from_focus():

    window = state.focused_window
    t_cursor = state.terminal.cursor
    if window:
        w_cursor = window.cursor
        t_cursor.hidden = w_cursor.hidden
        t_cursor.x = window.left + w_cursor.x
        t_cursor.y = window.top + w_cursor.y
    else:
        t_cursor.hidden = True



def render_focus_change():

    update_terminal_cursor_from_focus()
    state.terminal.render(cursor_only=True)



def destroy_task_windows(task):

    need_rerender = bool(state.task_windows[task])

    for window in state.task_windows[task]:
        state.all_windows.remove(window)
        state.cleanup_focusable_window_process(window)
    del state.task_windows[task]

    if need_rerender:
        rerender_all_windows()



def rerender_all_windows():

    state.terminal.clear()

    for w in state.all_windows:
        render_window_to_terminal(w, full=True)

    update_terminal_cursor_from_focus()
    state.terminal.render()


# ----------------------------------------------------------------------------
