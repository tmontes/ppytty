# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import task



class Parallel(task.Task):

    def __init__(self, tasks, stop_last=0, **kw):

        super().__init__(**kw)
        self._tasks = tasks
        self._stop_last = stop_last


    def run(self):

        running_tasks = []
        return_values = {}

        for task in self._tasks:
            yield ('task-spawn', task)
            running_tasks.append(task)
        while len(running_tasks) > self._stop_last:
            task, return_value = yield ('task-wait',)
            return_values[task] = return_value
            running_tasks.remove(task)
        for task in running_tasks:
            yield ('stop-task', task)
            _, _ = yield ('task-wait',)

        return return_values


    def reset(self):

        super().reset()
        for task in self._tasks:
            task.reset()


# ----------------------------------------------------------------------------
