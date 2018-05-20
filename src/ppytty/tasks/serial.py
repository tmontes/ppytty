# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import parallel
from . import task
from . import utils



class Serial(task.Task):

    _ACTIONS = ['next', 'prev', 'redo']

    def __init__(self, tasks, *, default_nav='next', return_nav_hint=True,
                 stop_when_under=True, stop_when_over=True, monitor_factory=None,
                 **kw):

        super().__init__(**kw)
        self._tasks = tasks
        self._default_nav = default_nav
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

            yield ('run-task', task)
            _, nav_hint = yield ('wait-task',)
            action = nav_hint if nav_hint in self._ACTIONS else self._default_nav

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
    def timed_monitor(seconds, monitored_name=None):

        def monitor_factory(monitored_task, current_index, max_index):

            tm_name = f'{monitored_name or ""}.{current_index}'
            st_name = f'{tm_name}.st'
            sleep_task = utils.DelayReturn(seconds=seconds, return_value='next', name=st_name)
            return _TaskMonitor(monitored_task, sleep_task, name=tm_name)

        return monitor_factory


    @staticmethod
    def keyboard_monitor(key_map=None, monitored_name=None):

        def monitor_factory(monitored_task, current_index, max_index):

            tm_name = f'{monitored_name or ""}.{current_index}'
            kt_name = f'{tm_name}.ka'
            keyboard_task = utils.KeyboardAction(keymap=key_map, name=kt_name)
            return _TaskMonitor(monitored_task, keyboard_task, name=tm_name)

        return monitor_factory



class _TaskMonitor(parallel.Parallel):

    def __init__(self, task, monitor_task, **kw):

        super().__init__([monitor_task, task], stop_last=1, **kw)


    def run(self):

        result = yield from super().run()
        if len(result) > 1:
            self._log.warn('more than one result: %r', result)
        return result.popitem()[1]


# ----------------------------------------------------------------------------
