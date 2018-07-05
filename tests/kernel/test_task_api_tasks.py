# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import (
    run, TrapException, TrapDoesNotExist, TrapArgCountWrong, TrapDestroyed,
)

from . import helper_io
from . import helper_state
from . import tasks



class TestSpawnWaitObjects(helper_io.NoOutputTestCase):

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



class TestWait(helper_io.NoOutputTestCase):

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



class TestWaitChildException(helper_io.NoOutputTestCase):

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



class TestSpawnDontWait(helper_io.NoOutputTestCase):

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



class TestSpawnDestroy(helper_io.NoOutputAutoTimeTestCase,
                       helper_state.StateAssertionsMixin):

    def _test_spawn_child_then_destroy(self, running):

        def child():
            yield ('sleep', 42)

        def parent(child_task):
            yield ('task-spawn', child_task)
            yield ('task-destroy', child_task)
            completed_task, child_success, child_result = yield ('task-wait',)
            return completed_task, child_success, child_result

        # Time starts at 0.
        self.assertEqual(self.auto_time.monotonic, 0)

        child_task = child() if running else child
        parent_task = parent(child_task)
        success, result = run(parent_task)
        self.assertTrue(success)

        completed_task, child_success, child_result = result
        self.assertIs(completed_task, child_task)
        self.assertFalse(child_success)
        self.assertIsInstance(child_result, TrapDestroyed)
        self.assertEqual(len(child_result.args), 1)
        self.assertIs(child_result.args[0], parent_task)

        # Time hasn't passed.
        self.assertEqual(self.auto_time.monotonic, 0)


    def test_spawn_child_then_destroy_gen_object(self):

        self._test_spawn_child_then_destroy(running=True)


    def test_spawn_child_then_destroy_gen_function(self):

        self._test_spawn_child_then_destroy(running=False)


    def test_spawn_child_subchildren_destroy(self):

        def sub_child_sleep(sleep_duration):
            yield ('sleep', sleep_duration)

        def sub_child_task_wait():
            yield ('task-wait',)

        def child():
            sub_child_task1 = sub_child_sleep(0)
            sub_child_task2 = sub_child_sleep(1)
            sub_child_task3 = sub_child_sleep(42)
            sub_child_task4 = sub_child_task_wait()
            yield ('task-spawn', sub_child_task1)
            yield ('task-spawn', sub_child_task2)
            yield ('task-spawn', sub_child_task3)
            yield ('task-spawn', sub_child_task4)
            _ = yield ('task-wait',)
            yield ('sleep', 420)

        def parent(child_task):
            yield ('task-spawn', child_task)
            yield ('sleep', 2)
            yield ('task-destroy', child_task)
            completed_task, child_success, child_result = yield ('task-wait',)
            return completed_task, child_success, child_result

        child_task = child()
        parent_task = parent(child_task)
        success, result = run(parent_task)

        self.assertTrue(success)
        completed_task, child_success, child_result = result
        self.assertIs(completed_task, child_task)
        self.assertEqual(child_success, False)
        self.assertIsInstance(child_result, TrapDestroyed)
        self.assertEqual(len(child_result.args), 1)
        self.assertIs(child_result.args[0], parent_task)

        self.assert_no_tasks()


    def test_cannot_destroy_sibling(self):

        def sleeping_sibling():
            yield ('sleep', 42)

        def destroyer_sibling():
            _, my_sibling = yield ('message-wait',)
            yield ('task-destroy', my_sibling)

        def parent(sleeper, destroyer):
            yield ('task-spawn', sleeper)
            yield ('task-spawn', destroyer)
            yield ('message-send', destroyer, sleeper)
            task_wait_1 = yield ('task-wait',)
            task_wait_2 = yield ('task-wait',)
            return task_wait_1, task_wait_2

        sleep_task = sleeping_sibling()
        destroyer_task = destroyer_sibling()

        success, result = run(parent(sleep_task, destroyer_task))
        self.assertTrue(success)

        task_wait_1, task_wait_2 = result

        # destroyer_task completes first (sleep_task is sleeping) and fails with
        # a TrapException mentioning 'child'.
        completed, success, result = task_wait_1
        self.assertIs(completed, destroyer_task)
        self.assertFalse(success)
        self.assertIsInstance(result, TrapException)
        self.assertGreaterEqual(len(result.args), 1)
        self.assertIn('child', result.args[0])

        completed, success, result = task_wait_2
        self.assertIs(completed, sleep_task)
        self.assertTrue(success)
        self.assertIsNone(result)


    def test_destroy_running_child(self):

        def child():
            while True:
                yield ('sleep', 0)

        def parent(child_task):
            yield ('task-spawn', child_task)
            yield ('task-destroy', child_task)
            completed_task, child_success, child_result = yield ('task-wait',)
            return completed_task, child_success, child_result

        parent_task = parent(child)
        success, result = run(parent_task)

        self.assertTrue(success)
        completed_task, child_success, child_result = result
        self.assertIs(completed_task, child)
        self.assertFalse(child_success)
        self.assertIsInstance(child_result, TrapDestroyed)
        self.assertGreaterEqual(len(child_result.args), 1)
        self.assertIs(child_result.args[0], parent_task)

        self.assert_no_tasks()


# ----------------------------------------------------------------------------
