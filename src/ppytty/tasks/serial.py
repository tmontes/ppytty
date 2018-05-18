# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import task
from . import utils



def mtf(monitored_task, current_index, max_index):

    class TaskMonitor(task.Task):

        def run(self):

            sleep_task = utils.DelayReturn(seconds=3, return_value='next')
            yield ('run-task', monitored_task)
            yield ('run-task', sleep_task)
            finished, return_value = yield ('wait-task',)
            stop = monitored_task if finished is sleep_task else sleep_task
            yield ('stop-task', stop)
            _, _ = yield ('wait-task',)
            return return_value

    return TaskMonitor()



class Serial(task.Task):

    _ACTIONS = ['next', 'prev', 'redo']

    def __init__(self, tasks, *, monitor_task_factory=mtf, **kw):

        super().__init__(**kw)
        self._tasks = tasks
        self._monitor_task_factory = monitor_task_factory


    def run(self):

        index = 0
        index_max = len(self._tasks) - 1

        while True:
            task = self._tasks[index]
            task.reset()
            if self._monitor_task_factory:
                task = self._monitor_task_factory(task, index, index_max)
            yield ('run-task', task)
            _, nav_hint = yield ('wait-task',)
            action = nav_hint if nav_hint in self._ACTIONS else 'next'

            if action == 'next':
                if index < index_max:
                    index += 1
                    continue
                else:
                    break
            elif action == 'prev':
                if index > 0:
                    index -= 1
                    continue
                else:
                    break


# ----------------------------------------------------------------------------
