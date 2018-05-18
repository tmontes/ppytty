# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import task



class Serial(task.Task):

    _ACTIONS = ['next', 'prev', 'redo', 'exit-next', 'exit-prev', 'exit-redo']

    def __init__(self, tasks, *, nav_task=None,
                 take_nav_hints=True, give_nav_hints=True,
                 stop_over=True, stop_under=True, **kw):

        super().__init__(**kw)
        self._tasks = tasks
        self._nav_task = nav_task
        self._take_nav_hints = take_nav_hints
        self._give_nav_hints = give_nav_hints
        self._stop_over = stop_over
        self._stop_under = stop_under


    def run(self):

        index = 0
        index_max = len(self._tasks) - 1

        while True:
            task = self._tasks[index]
            task.reset()
            yield ('run-task', task)
            _, nav_hint = yield ('wait-task',)
            action = 'next'
            if self._take_nav_hints:
                if nav_hint in self._ACTIONS:
                    action = nav_hint
                else:
                    action = None
            while True:
                if self._nav_task and action is None:
                    self._nav_task.reset()
                    yield ('run-task', self._nav_task)
                    _, action = yield ('wait-task',)
                    if action not in self._ACTIONS:
                        self._log.warning('invalid nav_task action %r', action)
                        action = None
                        continue
                if action == 'next':
                    if index < index_max:
                        index += 1
                        break
                    elif self._stop_over:
                        return action if self._give_nav_hints else None
                    else:
                        action = None
                        continue
                elif action == 'prev':
                    if index > 0:
                        index -= 1
                        break
                    elif self._stop_under:
                        return action if self._give_nav_hints else None
                    else:
                        action = None
                        continue
                elif action == 'redo':
                    break
                elif action and action.startswith('exit-') and self._give_nav_hints:
                    return action[5:]


# ----------------------------------------------------------------------------
