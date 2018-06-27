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



class TestSpawn(io_bypass.NoOutputTestCase):

    def test_spawn_gen_function(self):

        generator_function = tasks.sleep_zero
        task = tasks.spawn_wait(generator_function)
        run(task)


    def test_spawn_gen_object(self):

        generator_object = tasks.sleep_zero()
        task = tasks.spawn_wait(generator_object)
        run(task)



class TestWait(io_bypass.NoOutputTestCase):

    def test_wait_child_success(self):

        task = tasks.spawn_wait(tasks.sleep_zero_return_42_idiv_arg(42))
        parent_sucess, parent_result = run(task)
        self.assertTrue(parent_sucess)
        child_success, child_result = parent_result
        self.assertTrue(child_success)
        self.assertEqual(child_result, 1)


    def test_wait_child_exception(self):

        task = tasks.spawn_wait(tasks.sleep_zero_return_42_idiv_arg(0))
        parent_success, parent_result = run(task)
        self.assertTrue(parent_success)
        child_success, child_result = parent_result
        self.assertFalse(child_success)
        self.assertIsInstance(child_result, ZeroDivisionError)


# ----------------------------------------------------------------------------
