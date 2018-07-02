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



class TestSpawnWaitObjects(io_bypass.NoOutputTestCase):

    def test_spawn_wait_gen_function_child_completes_1st(self):

        generator_function = tasks.sleep_zero
        task = tasks.spawn_wait(generator_function)
        success, result = run(task)
        self.assertTrue(success)
        completed_child, child_success, child_result = result
        self.assertIs(completed_child, generator_function)
        self.assertTrue(child_success)
        self.assertIsNone(child_result)


    def test_spawn_wait_gen_object_child_completes_1st(self):

        generator_object = tasks.sleep_zero()
        task = tasks.spawn_wait(generator_object)
        success, result = run(task)
        self.assertTrue(success)
        completed_child, child_success, child_result = result
        self.assertIs(completed_child, generator_object)
        self.assertTrue(child_success)
        self.assertIsNone(child_result)


    def test_spawn_wait_gen_function_child_completes_2nd(self):

        generator_function = tasks.sleep_zero
        task = tasks.spawn_wait(generator_function, sleep_before_wait=True)
        success, result = run(task)
        self.assertTrue(success)
        completed_child, child_success, child_result = result
        self.assertIs(completed_child, generator_function)
        self.assertTrue(child_success)
        self.assertIsNone(child_result)


    def test_spawn_wait_gen_object_child_completes_2nd(self):

        generator_object = tasks.sleep_zero()
        task = tasks.spawn_wait(generator_object, sleep_before_wait=True)
        success, result = run(task)
        self.assertTrue(success)
        completed_child, child_success, child_result = result
        self.assertIs(completed_child, generator_object)
        self.assertTrue(child_success)
        self.assertIsNone(child_result)



class TestWait(io_bypass.NoOutputTestCase):

    def test_wait_child_success(self):

        task = tasks.spawn_wait(tasks.sleep_zero_return_42_idiv_arg(42))
        parent_sucess, parent_result = run(task)
        self.assertTrue(parent_sucess)
        _completed_child, child_success, child_result = parent_result
        self.assertTrue(child_success)
        self.assertEqual(child_result, 1)


    def test_wait_child_exception(self):

        task = tasks.spawn_wait(tasks.sleep_zero_return_42_idiv_arg(0))
        parent_success, parent_result = run(task)
        self.assertTrue(parent_success)
        _completed_child, child_success, child_result = parent_result
        self.assertFalse(child_success)
        self.assertIsInstance(child_result, ZeroDivisionError)



class TestWaitChildException(io_bypass.NoOutputTestCase):

    def parent_spawn_wait_child_exception(self, child_task, expected_exc_class):

        success, result = run(tasks.spawn_wait(child_task))
        self.assertTrue(success)
        completed_child, child_task_success, child_task_result = result
        self.assertIs(completed_child, child_task)
        self.assertFalse(child_task_success)
        self.assertIsInstance(child_task_result, expected_exc_class)
        return child_task_result


    def test_parent_spawn_wait_child_exception(self):

        def child():
            yield ('sleep', 0)
            return 1 // 0

        self.parent_spawn_wait_child_exception(child(), ZeroDivisionError)


    def test_parent_spawn_wait_child_trap_does_not_exist_exception(self):

        def child():
            yield ('this-trap-does-not-exist',)

        exc = self.parent_spawn_wait_child_exception(child(), TrapDoesNotExist)
        self.assertEqual(len(exc.args), 1)
        # Exception "message" should include the trap name.
        self.assertIn('this-trap-does-not-exist', exc.args[0])


    def test_parent_spawn_wait_child_trap_arg_count_wrong_exception(self):

        def child():
            yield ('sleep', 1, 2, 3)

        exc = self.parent_spawn_wait_child_exception(child(), TrapArgCountWrong)
        self.assertEqual(len(exc.args), 1)
        # Exception "message" should include 'argument', somehow.
        self.assertIn('argument', exc.args[0])



class TestSpawnDontWait(io_bypass.NoOutputTestCase):

    def test_parent_spawn_crash_no_child_wait_parent_completes_1st(self):

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


    def test_parent_spawn_crash_no_child_wait_parent_completes_2nd(self):

        def child():
            yield ('sleep', 0)
            return 42

        def parent():
            child_task = child()
            yield ('task-spawn', child_task)
            yield ('sleep', 0)
            raise RuntimeError('parent crashing before child task-wait')

        success, result = run(parent)
        self.assertFalse(success)
        self.assertIsInstance(result, RuntimeError)


    def test_child_spawn_crash_no_grand_child_wait_child_completes_1st(self):

        def grand_child():
            yield ('sleep', 0)

        def child():
            grand_child_task = grand_child()
            yield ('task-spawn', grand_child_task)
            raise RuntimeError('child crashing before grand child task-wait')

        def parent():
            child_task = child()
            yield ('task-spawn', child_task)
            completed_task, child_success, child_result = yield ('task-wait',)
            return completed_task is child_task, child_success, child_result

        success, result = run(parent)
        self.assertTrue(success)
        expected_task_completed, child_task_success, child_task_result = result
        self.assertTrue(expected_task_completed)
        self.assertFalse(child_task_success)
        self.assertIsInstance(child_task_result, RuntimeError)


    def test_child_spawn_crash_no_grand_child_wait_child_completes_2nd(self):

        def grand_child():
            yield ('sleep', 0)

        def child():
            grand_child_task = grand_child()
            yield ('task-spawn', grand_child_task)
            yield ('sleep', 0)
            raise RuntimeError('child crashing before grand child task-wait')

        def parent():
            child_task = child()
            yield ('task-spawn', child_task)
            completed_task, child_success, child_result = yield ('task-wait',)
            return completed_task is child_task, child_success, child_result

        success, result = run(parent)
        self.assertTrue(success)
        expected_task_completed, child_task_success, child_task_result = result
        self.assertTrue(expected_task_completed)
        self.assertFalse(child_task_success)
        self.assertIsInstance(child_task_result, RuntimeError)


# ----------------------------------------------------------------------------
