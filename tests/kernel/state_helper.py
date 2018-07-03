# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty.kernel.state import state



class StateAssertionsMixin(object):

    _TASK_CONTAINER_NAMES = (
        'runnable_tasks',
        'completed_tasks',
        'tasks_waiting_child',
        'tasks_waiting_inbox',
        'tasks_waiting_key',
        'tasks_waiting_time',
    )
    def assert_no_tasks(self):

        for task_container_name in StateAssertionsMixin._TASK_CONTAINER_NAMES:
            value = getattr(state, task_container_name)
            self.assertFalse(value, f'{task_container_name} not empty')


# ----------------------------------------------------------------------------