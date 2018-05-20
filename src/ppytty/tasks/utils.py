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


# ----------------------------------------------------------------------------
