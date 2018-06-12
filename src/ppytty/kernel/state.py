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


    # Keys: Tasks, Values: The last Task request, if any.
    requests = {},
    # Keys: Tasks, Values: The value to return to the task, if any.
    responses = {},
)



state = types.SimpleNamespace(

    # Global time.
    now = None,

    # Global input/output terminal.
    terminal = None,
)


# ----------------------------------------------------------------------------
