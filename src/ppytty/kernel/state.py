# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import collections



class _Base(object):

    def __init__(self):

        self.reset()


    def reset(self):

        raise NotImplementedError()



class _Tasks(_Base):

    def reset(self):

        # The task given to the scheduler, to be run.
        self.top_task = None

        # True if top_task completed, False otherwise (exception or interrupted).
        self.top_task_success = None

        # Exception if top_task_success is False, else whatever top_task returned.
        self.top_task_result = None

        # Runnable tasks queue.
        self.runnable = collections.deque()

        # Terminated tasks will be here until their parent task waits on them.
        self.terminated = []

        # Keys: Tasks, Values: Their parent Task.
        self.parent = {}
        # Keys: Tasks, Values: List of child Tasks, if any.
        self.children = collections.defaultdict(list)

        # Tasks waiting on children.
        self.waiting_child = []

        # Tasks waiting on keyboard input, and the associated priority queue.
        self.waiting_key = []
        self.waiting_key_hq = []

        # Tasks sleeping, and the associated priority queue.
        self.waiting_time = []
        self.waiting_time_hq = []

        # Keys: Tasks, Values: Their current trap, if any.
        self.trap_calls = {}
        # Keys: Tasks, Values: The value to return to the task, if any.
        self.trap_results = {}

        # Keys: Tasks, Values: List of Task created Windows.
        self.windows = collections.defaultdict(list)



class _IOFDs(_Base):

    def reset(self):

        self.input = []
        self.output = []
        self.user_in = None
        self.user_out = None


    def set_user_io(self, in_fd, out_fd):

        self.user_in = in_fd
        self.input.append(in_fd)
        self.user_out = out_fd
        self.output.append(out_fd)



class _State(_Base):

    def reset(self):

        # Global time.
        self.now = None

        # Interactive input/output user terminal.
        self.terminal = None

        # Task created Window list in back to front rendering order.
        self.all_windows = []



tasks = _Tasks()
io_fds = _IOFDs()
state = _State()



def reset():

    tasks.reset()
    io_fds.reset()
    state.reset()


# ----------------------------------------------------------------------------
