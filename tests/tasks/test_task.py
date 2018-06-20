# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

from ppytty import Task


class TestTask(unittest.TestCase):

    def setUp(self):

        self.task = Task(name='task-name')


    def test_repr_includes_class_name(self):

        value = repr(self.task)
        self.assertTrue(
            value.startswith('<Task '),
            'repr does not start with class name',
        )


    def test_repr_includes_name_repr(self):

        value = repr(self.task)
        self.assertIn(" 'task-name' ", value, 'repr does not contain task name')


    def test_running_task_raises_not_implemented(self):

        with self.assertRaises(NotImplementedError):
            self.task.running.send(None)



class _BasicTask(Task):

    def run(self):

        yield 1
        yield 2
        yield 3



class TestBasicTask(unittest.TestCase):

    def test_tasks_can_be_reset(self):

        task = _BasicTask(name='basic-task')

        first_value = task.running.send(None)
        self.assertEqual(1, first_value, 'first iteration value is wrong')

        second_value = task.running.send(None)
        self.assertEqual(2, second_value, 'first iteration value is wrong')

        task.reset()
        values = [v for v in task.running]
        self.assertEqual([1, 2, 3], values, 'second run values are wrong')


# ----------------------------------------------------------------------------