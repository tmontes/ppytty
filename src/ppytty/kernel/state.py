# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import collections
import types



tasks = types.SimpleNamespace(

    # The task given to the scheduler, to be run.
    top_task = None,

    # Runnable tasks queue.
    runnable = collections.deque(),

    # Terminated tasks will be here until their parent task waits on them.
    terminated = [],

    # Keys: Tasks, Values: Their parent Task.
    parent = {},
    # Keys: Tasks, Values: List of child Tasks, if any.
    children = collections.defaultdict(list),

    # Tasks waiting on children.
    waiting_on_child = [],

    # Tasks waiting on keyboard input, and the associated priority queue.
    waiting_on_key = [],
    waiting_on_key_hq = [],

    # Tasks sleeping, and the associated priority queue.
    waiting_on_time = [],
    waiting_on_time_hq = [],


    # Keys: Tasks, Values: Their current trap, if any.
    trap_calls = {},
    # Keys: Tasks, Values: The value to return to the task, if any.
    trap_results = {},


    # Keys: Tasks, Values: List of Task created Windows.
    windows = collections.defaultdict(list),
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

    # Task created Window list in back to front rendering order.
    all_windows = [],
)



def reset():

    tasks.top_task = None
    tasks.runnable = collections.deque()
    tasks.terminated = []
    tasks.parent = {}
    tasks.children = collections.defaultdict(list)
    tasks.waiting_on_child = []
    tasks.waiting_on_key = []
    tasks.waiting_on_key_hq = []
    tasks.waiting_on_time = []
    tasks.waiting_on_time_hq = []
    tasks.trap_calls = {}
    tasks.trap_results = {}
    tasks.windows = collections.defaultdict(list)

    io_fds.input = []
    io_fds.output = []
    io_fds.user_in = None
    io_fds.user_out = None

    state.now = None
    state.terminal = None
    state.all_windows = []


# ----------------------------------------------------------------------------
