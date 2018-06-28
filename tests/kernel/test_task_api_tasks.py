# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import run, TrapDoesNotExist, TrapArgCountWrong

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



class TestWaitChildException(io_bypass.NoOutputTestCase):

    def parent_spawn_wait_child_exception(self, child_task, expected_exc_class):

        def parent():
            yield ('task-spawn', child_task)
            completed_task, child_success, child_result = yield ('task-wait',)
            return completed_task is child_task, child_success, child_result

        success, result = run(parent)
        self.assertTrue(success)
        correct_task_completed, child_task_success, child_task_result = result
        self.assertTrue(correct_task_completed)
        self.assertFalse(child_task_success)
        self.assertIsInstance(child_task_result, expected_exc_class)


    def test_parent_spawn_wait_child_exception(self):

        def child():
            yield ('sleep', 0)
            return 1 // 0

        self.parent_spawn_wait_child_exception(child(), ZeroDivisionError)


    def test_parent_spawn_wait_child_trap_does_not_exist_exception(self):

        def child():
            yield ('this-trap-does-not-exist',)

        self.parent_spawn_wait_child_exception(child(), TrapDoesNotExist)


    def test_parent_spawn_wait_child_trap_arg_count_wrong_exception(self):

        def child():
            yield ('sleep', 1, 2, 3)

        self.parent_spawn_wait_child_exception(child(), TrapArgCountWrong)



class TestSpawnDontWait(io_bypass.NoOutputTestCase):

    def test_parent_spawn_and_crash_before_child_wait(self):

        def child():
            yield ('sleep', 0)
            return 42

        def parent():
            child_task = child()
            yield ('task-spawn', child_task)
            raise RuntimeError('parent crashing before child task-wait')

        success, result = run(parent)
        self.assertFalse(success)
        self.assertIsInstance(result, RuntimeError)


# ----------------------------------------------------------------------------
