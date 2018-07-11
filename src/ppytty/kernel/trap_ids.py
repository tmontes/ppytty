# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import enum



class Trap(enum.Enum):

    DIRECT_CLEAR = enum.auto()
    DIRECT_PRINT = enum.auto()

    WINDOW_CREATE = enum.auto()
    WINDOW_RENDER = enum.auto()
    WINDOW_DESTROY = enum.auto()

    SLEEP = enum.auto()

    KEY_READ = enum.auto()
    KEY_UNREAD = enum.auto()

    TASK_SPAWN = enum.auto()
    TASK_DESTROY = enum.auto()
    TASK_WAIT = enum.auto()

    MESSAGE_SEND = enum.auto()
    MESSAGE_WAIT = enum.auto()

    STATE_DUMP = enum.auto()


# ----------------------------------------------------------------------------
