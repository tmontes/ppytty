# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import run

from . import io_bypass
from . import tasks



class TestRun(io_bypass.NoOutputTestCase):

    def test_gen_function(self):

        generator_function = tasks.sleep_zero
        run(generator_function)


    def test_gen_object(self):

        generator_object = tasks.sleep_zero()
        run(generator_object)



class TestReturns(io_bypass.NoOutputTestCase):

    def test_task_return(self):

        success, result = run(tasks.sleep_zero_return_42_idiv_arg(42))
        self.assertTrue(success)
        self.assertEqual(result, 1)


    def test_task_exception(self):

        success, result = run(tasks.sleep_zero_return_42_idiv_arg(0))
        self.assertFalse(success)
        self.assertIsInstance(result, ZeroDivisionError)


# ----------------------------------------------------------------------------
