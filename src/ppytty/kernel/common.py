# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import state



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



def highlight_focused_window(clear=False):

    window = state.focused_window
    if window is None:
        window = state.terminal.window

    window.highlight(clear=clear)

    rerender_all_windows(clear=clear)



def destroy_task_windows(task):

    need_rerender = bool(state.task_windows[task])

    for window in state.task_windows[task]:
        state.all_windows.remove(window)
        state.cleanup_focusable_window_process(window)
    del state.task_windows[task]

    if need_rerender:
        rerender_all_windows()



def rerender_all_windows(clear=True):

    # Speed up attribute access
    state_terminal = state.terminal
    state_terminal_feed = state_terminal.feed

    if clear:
        state_terminal.clear()

    for w in state.all_windows:
        state_terminal_feed(w.render(full=True))

    update_terminal_cursor_from_focus()
    state_terminal.render()


# ----------------------------------------------------------------------------
