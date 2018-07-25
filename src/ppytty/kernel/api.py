# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
Kernel Trap API

Running tasks use these to interact with the kernel.
"""

import types

from . traps import Trap



@types.coroutine
def direct_clear():
    """
    Clear the output TTY, bypassing kernel terminal/window handling.
    """
    yield Trap.DIRECT_CLEAR,



@types.coroutine
def direct_print(text, x=None, y=None, save_location=False):
    """
    Print to the output TTY, bypassing kernel terminal/window handling.
    """
    yield Trap.DIRECT_PRINT, text, x, y, save_location



@types.coroutine
def window_create(x, y, w, h, dx=0, dy=0, dw=0, dh=0, bg=None):
    """
    Creates a kernel managed window.
    """
    return (yield Trap.WINDOW_CREATE, x, y, w, h, dx, dy, dw, dh, bg)




@types.coroutine
def window_destroy(window):
    """
    Destroys `window`. If it has been rendered, the output terminal will be
    updated to reflect its destruction.

    Raises TrapException if `window` is not a caller task created window.
    """
    yield Trap.WINDOW_DESTROY, window



@types.coroutine
def window_render(window, full=False, terminal_render=True):
    """
    Renders `window` onto the output terminal.
    If `full` is True, the whole window contents is rendered; otherwise, only
    the lines that changed since the previous render will be rendered.
    If `terminal_render` is True, the terminal is rendered to the output TTY;
    this allows tasks to optimize rendering multiple windows to the terminal
    while only triggering the final terminal to TTY rendering at the end.
    """
    yield Trap.WINDOW_RENDER, window, full, terminal_render



@types.coroutine
def sleep(seconds):
    """
    Sleep caller for `seconds` seconds.
    """
    yield Trap.SLEEP, seconds



@types.coroutine
def key_read():
    """
    Blocks caller task, waiting for the kernel managed TTY input.
    Returns one or more bytes.

    Concurrent reads are served on a round-robin basis.
    """
    return (yield Trap.KEY_READ,)



@types.coroutine
def key_unread(pushed_back_bytes):
    """
    See `key_read`.
    """
    yield Trap.KEY_UNREAD, pushed_back_bytes



@types.coroutine
def task_spawn(task):
    """
    Spawns a new task as a child of the caller.
    """
    yield Trap.TASK_SPAWN, task



@types.coroutine
def task_wait():
    """
    Waits for child task completion.
    Returns (completed_task, success, result) tuple.
    """
    return (yield Trap.TASK_WAIT,)



@types.coroutine
def task_destroy(task):
    """
    Destroys `task` and all its children regardless of their state.
    Raises a TrapException if the given `task` is not a child of the caller.

    The destroyed `task` must still be waited for with a `task_wait` call:
    the `success` will be `False` and `result` will a TrapDestroyed instance.
    """
    yield Trap.TASK_DESTROY, task



@types.coroutine
def message_send(task, message):
    """
    Sends `message` to `task`. When `task` is None, sends `message to parent.
    """
    yield Trap.MESSAGE_SEND, task, message



@types.coroutine
def message_wait():
    """
    Waits for a message to be received.
    Returns (sender_task, message) tuple.
    """
    return (yield Trap.MESSAGE_WAIT,)



@types.coroutine
def process_spawn(window, args):
    """
    Spawns a child process with its stdin/out/err wired to a PTY in `window`.
    `args` should be a list where the first item is the executable and the
    remaining will be passed to it as command line arguments.

    Returns a process object.
    """
    return (yield Trap.PROCESS_SPAWN, window, args)


@types.coroutine
def process_wait():
    """
    Waits for a child process to terminate.
    Returns a (process, exit_code) tuple.
    """
    return (yield Trap.PROCESS_WAIT,)


@types.coroutine
def state_dump(tag=''):
    """
    Dumps the kernel state to the log, tagged with the optional `tag`.
    """
    yield Trap.STATE_DUMP, tag



# ----------------------------------------------------------------------------
