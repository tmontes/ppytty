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



@types.coroutine
def direct_clear():
    """
    Clear the output TTY, bypassing kernel terminal/window handling.
    """
    yield 'direct-clear',



@types.coroutine
def direct_print(text, x=None, y=None, save_location=False):
    """
    Print to the output TTY, bypassing kernel terminal/window handling.
    """
    yield 'direct-print', text, x, y, save_location



@types.coroutine
def window_create(left, top, width, height, background=None):
    """
    Creates a kernel managed window.
    """
    return (yield 'window-create', left, top, width, height, background)




@types.coroutine
def window_destroy(window):
    """
    Destroys `window`. If it has been rendered, the output terminal will be
    updated to reflect its destruction.

    Raises TrapException if `window` is not a caller task created window.
    """
    yield 'window-destroy', window



@types.coroutine
def window_render(window, full=False):
    """
    Renders `window` onto the output terminal.
    If `full` is True, the whole window contents is rendered; otherwise, only
    the lines that changed since the previous render will be rendered.
    """
    yield 'window-render', window, full



@types.coroutine
def sleep(seconds):
    """
    Sleep caller for `seconds` seconds.
    """
    yield 'sleep', seconds



@types.coroutine
def key_read(priority=0):
    """
    Blocks caller task, waiting for the kernel managed TTY input.
    Returns a single byte value.

    Concurrent reads are served on a `priority` basis: outstanding reads with
    lower numeric `priority` are served first. High priority readers can pass
    read byte values to lower priority ones via the `key_unread` trap.
    """
    return (yield 'key-read', priority)



@types.coroutine
def key_unread(key_byte_value):
    """
    See `key_read`.
    """
    yield 'key-unread', key_byte_value



@types.coroutine
def task_spawn(task):
    """
    Spawns a new task as a child of the caller.
    """
    yield 'task-spawn', task



@types.coroutine
def task_wait():
    """
    Waits for child task completion.
    Returns (completed_task, success, result) tuple.
    """
    return (yield 'task-wait',)



@types.coroutine
def task_destroy(task):
    """
    Destroys `task` and all its children regardless of their state.
    Raises a TrapException if the given `task` is not a child of the caller.

    The destroyed `task` must still be waited for with a `task_wait` call:
    the `success` will be `False` and `result` will a TrapDestroyed instance.
    """
    yield 'task-destroy', task



@types.coroutine
def message_send(task, message):
    """
    Sends `message` to `task`. When `task` is None, sends `message to parent.
    """
    yield 'message-send', task, message



@types.coroutine
def message_wait():
    """
    Waits for a message to be received.
    Returns (sender_task, message) tuple.
    """
    return (yield 'message-wait',)



@types.coroutine
def state_dump(tag=''):
    """
    Dumps the kernel state to the log, tagged with the optional `tag`.
    """
    yield 'state-dump', tag



# ----------------------------------------------------------------------------
