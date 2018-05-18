# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import task



class Parallel(task.Task):

    def __init__(self, tasks, **kw):

        super().__init__(**kw)
        self._tasks = tasks


    def run(self):

        running_tasks = []

        for task in self._tasks:
            yield ('run-task', task)
            running_tasks.append(task)
        while running_tasks:
            task, return_action = yield ('wait-task',)
            running_tasks.remove(task)

        if len(self._tasks) == 1:
            return return_action


    def reset(self):

        super().reset()
        for task in self._tasks:
            task.reset()


# ----------------------------------------------------------------------------
