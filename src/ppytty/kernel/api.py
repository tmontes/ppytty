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
def window_create(left, top, width, height, background=None):
    """
    Creates a kernel managed window.
    """
    return (yield Trap.WINDOW_CREATE, left, top, width, height, background)




@types.coroutine
def window_destroy(window):
    """
    Destroys `window`. If it has been rendered, the output terminal will be
    updated to reflect its destruction.

    Raises TrapException if `window` is not a caller task created window.
    """
    yield Trap.WINDOW_DESTROY, window



@types.coroutine
def window_render(window, full=False):
    """
    Renders `window` onto the output terminal.
    If `full` is True, the whole window contents is rendered; otherwise, only
    the lines that changed since the previous render will be rendered.
    """
    yield Trap.WINDOW_RENDER, window, full



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
    Returns a single byte value.

    Concurrent reads are served on a round-robin basis.
    """
    return (yield Trap.KEY_READ,)



@types.coroutine
def key_unread(key_byte_value):
    """
    See `key_read`.
    """
    yield Trap.KEY_UNREAD, key_byte_value



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
def state_dump(tag=''):
    """
    Dumps the kernel state to the log, tagged with the optional `tag`.
    """
    yield Trap.STATE_DUMP, tag



# ----------------------------------------------------------------------------
