# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

from ppytty.kernel import run, api
from ppytty.lib import Task



class TestTask(unittest.TestCase):

    def setUp(self):

        self.task = Task(id='task-id')


    def test_repr_includes_class_name(self):

        value = repr(self.task)
        self.assertTrue(
            value.startswith('<Task '),
            'repr does not start with class name',
        )


    def test_repr_includes_name_repr(self):

        value = repr(self.task)
        self.assertIn("'task-id'", value, 'repr does not contain task id')



class TestWithKernel(unittest.TestCase):

    def test_running_plain_task_raises_not_implemented(self):

        task = Task()

        success, result = run(task)
        self.assertFalse(success, 'should not have succeeded')
        self.assertIsInstance(result, NotImplementedError)


    def test_tasks_are_runnable(self):

        class SleepZero(Task):
            async def run(self):
                await api.sleep(0)

        task = SleepZero()

        success, result = run(task)
        self.assertTrue(success, 'should have succeeded')
        self.assertEqual(result, None)


    def test_tasks_can_be_reset(self):

        class Return42(Task):
            async def run(self):
                return 42

        task = Return42()

        success, result = run(task)
        self.assertTrue(success, 'should have succeeded')
        self.assertEqual(result, 42)

        success, result = run(task)
        self.assertFalse(success, 'should not have succeeded')
        self.assertIsInstance(result, RuntimeError)
        # With CPython 3.6.6: "cannot reuse already awaited coroutine"
        message = result.args[0]
        self.assertIn('reuse', message)
        self.assertIn('await', message)
        self.assertIn('coroutine', message)

        task.reset()
        success, result = run(task)
        self.assertTrue(success, 'should have succeeded')
        self.assertEqual(result, 42)


# ----------------------------------------------------------------------------
