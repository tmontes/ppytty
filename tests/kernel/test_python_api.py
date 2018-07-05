# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import run

from . import helper_io
from . import tasks



class TestRun(helper_io.NoOutputAutoTimeControlledInputTestCase):

    def test_gen_function(self):

        generator_function = tasks.sleep_zero
        run(generator_function)


    def test_gen_object(self):

        generator_object = tasks.sleep_zero()
        run(generator_object)


    def test_run_with_prompt_needs_double_q_to_complete(self):

        self.input_control.feed_data(b'qq!')

        run(tasks.sleep_zero, post_prompt='[COMPLETED]')

        # Check first two b'q' in the input were consumed: buffer holds b'!'.
        self.assertTrue(len(self.input_control.buffer), 1)
        self.assertEqual(self.input_control.buffer[0], b'!')



class TestReturns(helper_io.NoOutputTestCase):

    def test_task_return(self):

        success, result = run(tasks.sleep_zero_return_42_idiv_arg(42))
        self.assertTrue(success)
        self.assertEqual(result, 1)


    def test_task_exception(self):

        success, result = run(tasks.sleep_zero_return_42_idiv_arg(0))
        self.assertFalse(success)
        self.assertIsInstance(result, ZeroDivisionError)


# ----------------------------------------------------------------------------
