# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty.kernel import run
from ppytty.kernel.exceptions import TrapException

from . import helper_io
from . import helper_log
from . import helper_state



class TestNeedingOutput(unittest.TestCase):

    def setUp(self):

        self.log_handler = helper_log.create_and_add_handler()


    def tearDown(self):

        helper_log.remove_handler(self.log_handler)


    # Using helper_io.NoOutputTestCase makes this test fail.
    # Motive:
    # - state.user_out_fd would be a callable mock.
    # - The trap implementation excludes any callable attribute.

    # TODO: Maybe we can get back to a no-output producing test when the
    # input tests and associated input fakes are created.

    def test_state_dump_logs_all_state_fields(self):

        def task():
            yield ('state-dump',)

        success, result = run(task)

        self.assertTrue(success)
        self.assertIsNone(result)

        for state_attr in helper_state.STATE_ATTRS:
            with self.subTest(state_attr=state_attr):
                expected_pattern = f'state.{state_attr}='
                for message in self.log_handler.messages:
                    if expected_pattern in message:
                        break
                else:
                    raise AssertionError(f'{expected_pattern!r} not found')


class Test(helper_io.NoOutputAutoTimeTestCase):

    def setUp(self):

        super().setUp()
        self.log_handler = helper_log.create_and_add_handler()


    def tearDown(self):

        helper_log.remove_handler(self.log_handler)
        super().tearDown()


    def _assert_state_dump_logs_top_task(self, runnable=False):

        def task():
            yield('state-dump',)

        user_level_task = task() if runnable else task
        success, result = run(user_level_task)

        self.assertTrue(success)
        self.assertIsNone(result)

        expected = str(user_level_task)
        for message in self.log_handler.messages:
            if expected in message:
                break
            if 'DATA STRUCTURES' in message:
                # if we get to this point, the task hierarchy is gone
                raise AssertionError(f'{expected!r} not found')
        else:
            raise AssertionError(f'{expected!r} not found')


    def test_state_dump_logs_top_task_gen_function(self):

        self._assert_state_dump_logs_top_task(runnable=False)


    def test_state_dump_logs_top_task_gen_object(self):

        self._assert_state_dump_logs_top_task(runnable=True)


    def test_state_dump_logs_correct_task_states(self):

        def sleeping():
            yield ('sleep', 42)

        def wait_child():
            yield ('task-spawn', sleeping)
            yield ('task-wait',)

        def wait_inbox():
            yield ('message-wait',)

        def wait_key():
            yield ('read-key', 1000)

        def completed():
            yield ('sleep', 0)

        def runnable():
            yield ('sleep', 0)

        def parent():
            # Nuance: `runnable` spawned last means it will still be in the
            # runnable state when the `state-dump` trap is called.
            all_tasks = (wait_child, wait_inbox, wait_key, completed, runnable)
            for task in all_tasks:
                yield ('task-spawn', task)

            yield ('state-dump',)

            for task in all_tasks:
                try:
                    yield ('task-destroy', task)
                except TrapException:
                    # the `completed` task triggers this: it was waited by one
                    # of the previous `task-waits` and it no longer exists.
                    pass
                finally:
                    yield ('task-wait',)

        success, result = run(parent)

        self.assertTrue(success)
        self.assertIsNone(result)

        expected_states = {
            parent: 'RR',       # actually running, having called `state-dump`
            sleeping: 'WT',     # waiting on time via `sleep`
            wait_child: 'WC',   # waiting child via `task-wait`
            wait_inbox: 'WM',   # waiting message via `message-wait`
            wait_key: 'WK',     # waiting keyboard via `read-key`
            completed: 'CC',    # completed, not waited for yet
            runnable: 'RN',     # runnable, no chance to run yet
        }
        for task, expected_state in expected_states.items():
            with self.subTest(task=task, expected_state=expected_state):
                task_str = str(task)
                for message in self.log_handler.messages:
                    if task_str in message and expected_state in message:
                        break
                    if 'DATA STRUCTURES' in message:
                        # if we get to this point, the task hierarchy is gone
                        raise AssertionError(f'matching task/state not found')
                else:
                    # Should not be reached because `state-dump` output should
                    # include a 'DATA STRUCTURES' line, after the task state
                    # lines; keeping it here, just in case, with an *explicitly*
                    # different assertion error message.
                    raise AssertionError('no DATA STRUCTURES line in log')


# ----------------------------------------------------------------------------
