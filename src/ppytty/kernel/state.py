# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import collections
import types



tasks = types.SimpleNamespace(

    # TODO: Discarding this one - just used as "dump state" starting point.
    top_task = None,

    # Running tasks queue.
    running = collections.deque(),

    # Termminated tasks will be here until their parent task waits on them.
    terminated = [],

    # Keys: Tasks, Values: Respective parent Task.
    parent = {},
    # Keys: Tasks, Values: List of child Tasks, if any.
    children = collections.defaultdict(list),

    # Tasks waiting on children.
    waiting_on_child = [],

    # Tasks waiting on keyboard input.
    waiting_on_key = [],
    # The associated priority queue.
    waiting_on_key_hq = [],

    # Tasks sleeping.
    waiting_on_time = [],
    # The associated priority queue.
    waiting_on_time_hq = [],


    # Keys: Tasks, Values: The current Task trap, if any.
    trap_calls = {},
    # Keys: Tasks, Values: The value to return to the task, if any.
    trap_results = {},
)



class io_fds(object):

    input = []
    output = []
    user_in = None
    user_out = None

    # Would be more Pythonic with class-level properties for `user_in` and
    # `user_out`: that would require a meta-class and maybe that's too much
    # for such a simple, single-use, use case.

    @classmethod
    def set_user_io(cls, in_fd, out_fd):
        cls.user_in = in_fd
        cls.input.append(in_fd)
        cls.user_out = out_fd
        cls.output.append(out_fd)



state = types.SimpleNamespace(

    # Global time.
    now = None,

    # Interactive input/output user terminal.
    terminal = None,
)


# ----------------------------------------------------------------------------
