# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import run

from . import io_bypass
from . import log_helper
from . import state_helper



class Test(unittest.TestCase):

    def setUp(self):

        self.log_handler = log_helper.create_and_add_handler()


    def tearDown(self):

        log_helper.remove_handler(self.log_handler)


    # Using io_bypass.NoOutputTestCase makes this test fail.
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

        for state_attr in state_helper.STATE_ATTRS:
            with self.subTest(state_attr=state_attr):
                expected_pattern = f'state.{state_attr}='
                for message in self.log_handler.messages:
                    if expected_pattern in message:
                        break
                else:
                    raise AssertionError(f'{expected_pattern!r} not found')


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

# ----------------------------------------------------------------------------
