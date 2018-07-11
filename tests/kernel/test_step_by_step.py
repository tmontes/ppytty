# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
Step by step kernel loop tests
"""

# These tests are mostly put in place as a demonstration of low-level
# kernel testability. Whether this kind of testability will be put to
# use is not clear at this moment.
#
# Most kernel testing is done from an integration standpoint: running the loop
# with select tasks, invoking various kernel traps/apis, and asserting the
# results.

from ppytty.kernel import loop, terminal, api
from ppytty.kernel.state import state

from . import helper_io



class Test(helper_io.NoOutputAutoTimeTestCase):

    def _assert_not_completed(self, success, result):

        self.assertIsNone(success, 'success should be None')
        self.assertIsNone(result, 'result should be None')


    def _assert_runnable_not_waiting(self):

        self.assertTrue(state.runnable_tasks, 'no runnable tasks')
        self.assertFalse(state.tasks_waiting_time, 'tasks waiting for time')


    def _assert_waiting_not_runnable(self):

        self.assertFalse(state.runnable_tasks, 'found runnable tasks')
        self.assertTrue(state.tasks_waiting_time, 'no tasks waiting for time')


    def test_step_by_step_single_task_sleep(self):

        async def sleeper():

            await api.sleep(5)
            return 42

        # --------------------------------------------------------------------
        # Preparation for running
        # - now is None
        # - Task is in runnable_tasks and not in tasks_waiting_time.

        state.prepare_to_run(sleeper, terminal.Terminal())
        self.assertIs(state.now, None, 'unexpected state.now')
        self._assert_runnable_not_waiting()

        # --------------------------------------------------------------------
        # Iteration #1
        # - now is still 0.
        # - Task will be moved from runnable_tasks to tasks_waiting_time.

        success, result = loop.loop(once=True)
        self._assert_not_completed(success, result)
        self.assertEqual(state.now, 0, 'unexpected state.now')
        self._assert_waiting_not_runnable()

        # --------------------------------------------------------------------
        # Iteration #2
        # - Low level io call waits 5 seconds.

        success, result = loop.loop(once=True)
        self._assert_not_completed(success, result)
        self.assertEqual(state.now, 0, 'unexpected state.now')
        self._assert_waiting_not_runnable()

        # Iteration #3

        # success, result = loop.loop(once=True)
        # self._assert_not_completed(success, result)
        # self.assertEqual(state.now, 5, 'unexpected state.now')
        # self._assert_runnable_not_waiting()

        # --------------------------------------------------------------------
        # Iteration #3
        # - now is 5 seconds later.
        # - Completed with success and the return value of the task.

        success, result = loop.loop(once=True)
        self.assertEqual(state.now, 5, 'unexpected state.now')
        self.assertTrue(success)
        self.assertEqual(result, 42)


# ----------------------------------------------------------------------------
