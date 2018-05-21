# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import task



class DelayReturn(task.Task):

    def __init__(self, *, seconds=0, return_value=None, **kw):

        super().__init__(**kw)
        self._seconds = seconds
        self._return_value = return_value


    def run(self):

        yield ('sleep', self._seconds)
        return self._return_value



class KeyboardAction(task.Task):

    def __init__(self, keymap, default_action=None, **kw):

        super().__init__(**kw)
        self._keymap = keymap
        self._default_action = default_action


    def run(self):

        key = yield ('read-key',)
        return self._keymap.get(key, self._default_action)



class Loop(task.Task):

    def __init__(self, task, times=None, **kw):

        self._task = task
        self._times = times
        super().__init__(**kw)


    def run(self):

        times_to_go = self._times
        while times_to_go is None or times_to_go:
            self._task.reset()
            yield ('run-task', self._task)
            _, _ = yield ('wait-task',)
            if times_to_go is not None:
                times_to_go -= 1



TASK = object()



class MasterSlave(task.Task):

    def __init__(self, master, slave, **kw):

        super().__init__(*kw)
        self._master = master
        self._slave = slave


    def run(self):

        yield ('run-task', self._master)
        yield ('run-task', self._slave)

        completed_first, value = yield('wait-task',)
        if completed_first is self._master:
            yield ('stop-task', self._slave)
            return_value = value
            expected_second = self._slave
        elif completed_first is self._slave:
            expected_second = self._master
        else:
            self._log.error('unexpected first completed: %r', completed_first)

        completed_second, value = yield ('wait-task',)
        if completed_second is not expected_second:
            self._log.error('unexpected second completed: %r', completed_second)
        if completed_second is self._master:
            return_value = value
        elif completed_second is self._slave:
            pass
        else:
            self._log.error('unexpected second completed: %r', completed_second)

        return return_value



class RunForAtLeast(task.Task):

    def __init__(self, task, seconds, return_early=TASK, return_late=TASK, **kw):

        super().__init__(**kw)
        self._task = task
        self._seconds = seconds
        self._return_early = return_early
        self._return_late = return_late


    def run(self):

        timeout_task = DelayReturn(seconds=self._seconds)

        yield ('run-task', timeout_task)
        yield ('run-task', self._task)

        completed_first, value = yield ('wait-task',)
        if completed_first is self._task:
            return_value = value if self._return_early is TASK else self._return_early
            expected_second = timeout_task
        elif completed_first is timeout_task:
            expected_second = self._task

        completed_second, value = yield ('wait-task',)
        if completed_second is not expected_second:
            self._log.error('unexpected second completed: %r', completed_second)
        if completed_second is self._task:
            return_value = value if self._return_late is TASK else self._return_late

        return return_value



class RunForAtMost(task.Task):

    def __init__(self, task, seconds, return_early=TASK, return_late='timeout', **kw):

        super().__init__(**kw)
        self._task = task
        self._seconds = seconds
        self._return_early = return_early
        self._return_late = return_late


    def run(self):

        timeout_task = DelayReturn(seconds=self._seconds)

        yield ('run-task', timeout_task)
        yield ('run-task', self._task)

        completed_first, value = yield ('wait-task',)
        if completed_first is self._task:
            stop_second = timeout_task
            return_value = value if self._return_early is TASK else self._return_early
        elif completed_first is timeout_task:
            stop_second = self._task

        yield ('stop-task', stop_second)
        completed_second, value = yield ('wait-task',)
        if completed_second is not stop_second:
            self._log.error('unexpected second completed: %r', completed_second)
        if completed_second is self._task:
            return_value = self._return_late

        return return_value


# ----------------------------------------------------------------------------
