# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import collections



class _State(object):

    def __init__(self):

        # ---------------------------------------------------------------------
        # Task state tracking.

        # The task given to the scheduler, to be run.
        self.top_task = None

        # True if top_task completed, False otherwise (exception or interrupted).
        self.top_task_success = None

        # Exception if top_task_success is False, else whatever top_task returned.
        self.top_task_result = None

        # Runnable tasks queue.
        self.runnable_tasks = collections.deque()

        # Completed tasks will be here until their parent task waits on them.
        # Keys: Tasks, Values: (success, result) tuple.
        self.completed_tasks = {}

        # Keys: Tasks, Values: Their parent Task.
        self.parent_task = {}
        # Keys: Tasks, Values: List of child Tasks, if any.
        self.child_tasks = collections.defaultdict(list)

        # Tasks waiting on children.
        self.tasks_waiting_child = []

        # Tasks waiting on their inbox.
        self.tasks_waiting_inbox = []

        # Tasks waiting on keyboard input, and the associated priority queue.
        self.tasks_waiting_key = []
        self.tasks_waiting_key_hq = []

        # Tasks sleeping, and the associated priority queue.
        self.tasks_waiting_time = []
        self.tasks_waiting_time_hq = []

        # ---------------------------------------------------------------------
        # Spawned objects

        # Maps running tasks to objects passed to scheduler.run / task-spawn.
        self.user_space_tasks = {}

        # Maps user space tasks (passed to run/task-spawn) to running tasks.
        self.kernel_space_tasks = {}

        # ---------------------------------------------------------------------
        # Task trap tracking.

        # The self.trap_... dicts have Tasks as their keys.

        # Values: Current trap, if any.
        self.trap_call = {}
        # Values: True means trap completed, False means trap failed.
        self.trap_success = {}
        # Values: Return values if success, Exception to throw otherwise.
        self.trap_result = {}

        # ---------------------------------------------------------------------
        # Task owned objects.

        # Keys: Tasks, Values: Ordered queue of (sender, message) tuples.
        self.task_inbox = collections.defaultdict(collections.deque)

        # Keys: Tasks, Values: List of Task created Windows.
        self.task_windows = collections.defaultdict(list)

        # Task created Window list in back to front rendering order.
        self.all_windows = []

        # ---------------------------------------------------------------------
        # I/O file descriptors.

        self.in_fds = []
        self.out_fds = []
        self.user_in_fd = None
        self.user_out_fd = None

        # ---------------------------------------------------------------------
        # Environment.

        # Global time.
        self.now = None

        # Interactive input/output user terminal.
        self.terminal = None


    def reset(self):

        self.__init__()


    def reset_for_terminal(self, terminal):

        self.__init__()
        self.terminal = terminal
        self.user_in_fd = terminal.in_fd
        self.in_fds.append(terminal.in_fd)
        self.user_out_fd = terminal.out_fd
        self.out_fds.append(terminal.out_fd)



state = _State()


# ----------------------------------------------------------------------------
