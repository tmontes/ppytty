# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run

from . import io_bypass
from . import log_helper
from . import state_helper



class Test(io_bypass.NoOutputTestCase):

    def test_state_dump_logs_all_state_fields(self):

        def task():
            yield ('state-dump',)

        log_handler = log_helper.create_and_add_handler()
        self.addCleanup(lambda: log_helper.remove_handler(log_handler))

        success, result = run(task)

        self.assertTrue(success)
        self.assertIsNone(result)

        for state_attr in state_helper.STATE_ATTRS:
            with self.subTest(state_attr=state_attr):
                expected_pattern = f'state.{state_attr}='
                for message in log_handler.messages:
                    if expected_pattern in message:
                        break
                else:
                    raise AssertionError(f'{expected_pattern!r} not found')


# ----------------------------------------------------------------------------
