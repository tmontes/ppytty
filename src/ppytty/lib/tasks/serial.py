# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import task
from . import utils



class Serial(task.Task):

    _ACTIONS = ['next', 'prev', 'redo']

    def __init__(self, tasks, *, default_nav='next', take_nav_hint=True,
                 return_nav_hint=True, stop_when_under=True, stop_when_over=True,
                 monitor_factory=None,
                 **kw):

        super().__init__(**kw)
        self._tasks = tasks
        self._default_nav = default_nav
        self._take_nav_hint = take_nav_hint
        self._return_nav_hint = return_nav_hint
        self._stop_when_under = stop_when_under
        self._stop_when_over = stop_when_over
        self._monitor_factory = monitor_factory


    def run(self):

        index = 0
        index_max = len(self._tasks) - 1
        last_run_index = None
        do_nothing = utils.Loop(utils.DelayReturn(seconds=3600), name='nothing')

        while True:
            task = self._tasks[index] if index != last_run_index else do_nothing
            task.reset()
            if self._monitor_factory:
                task = self._monitor_factory(task, index, index_max)

            yield ('task-spawn', task)
            _, nav_hint = yield ('task-wait',)

            action = self._default_nav
            if self._take_nav_hint and nav_hint in self._ACTIONS:
                action = nav_hint

            last_run_index = index

            if action == 'next':
                if index < index_max:
                    index += 1
                    continue
                elif self._stop_when_over:
                    return action if self._return_nav_hint else None
            elif action == 'prev':
                if index > 0:
                    index -= 1
                    continue
                elif self._stop_when_under:
                    return action if self._return_nav_hint else None
            elif action == 'redo':
                last_run_index = None


    @staticmethod
    def time_monitor(min_seconds, max_seconds, monitored_name=None):

        if min_seconds > max_seconds:
            raise ValueError('invalid min_seconds > max_seconds')

        def monitor_factory(monitored_task, current_index, max_index):

            monitor_name = f'{monitored_name or ""}.{current_index}'
            min_duration_task = utils.RunForAtLeast(
                monitored_task, min_seconds,
                return_early='next', return_late='next',
                name=monitor_name,
            )
            max_duration_task = utils.RunForAtMost(
                min_duration_task, max_seconds,
                return_early='next', return_late='next',
                name=monitor_name,
            )
            return max_duration_task

        return monitor_factory


    @staticmethod
    def keyboard_monitor(action_map=None, priority=0, monitored_name=None):

        def monitor_factory(monitored_task, current_index, max_index):

            monitor_name = f'{monitored_name or ""}.{current_index}'
            if callable(action_map):
                effective_action_map = action_map(current_index, max_index)
            else:
                effective_action_map = action_map
            keyboard_task = utils.KeyboardAction(effective_action_map, priority, name=monitor_name)
            return utils.MasterSlave(keyboard_task, monitored_task, name=monitor_name)

        return monitor_factory


# ----------------------------------------------------------------------------