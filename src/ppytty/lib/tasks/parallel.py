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


    async def run(self):

        running_tasks = []
        results = {}

        for task in self._tasks:
            await self.api.task_spawn(task)
            running_tasks.append(task)
        while len(running_tasks) > self._stop_last:
            task, success, return_value = await self.api.task_wait()
            results[task] = (success, return_value)
            running_tasks.remove(task)
        for task in running_tasks:
            await self.api.task_destroy(task)
            _ = await self.api.task_wait()

        return results


    def reset(self):

        super().reset()
        for task in self._tasks:
            task.reset()


# ----------------------------------------------------------------------------
