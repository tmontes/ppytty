# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run, TrapDoesNotExist, TrapArgCountWrong

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    def test_non_existing_trap_raises_exception(self):

        def task():
            yield ('no-such-trap',)

        success, result = run(task)
        self.assertFalse(success)
        self.assertIsInstance(result, TrapDoesNotExist)
        exception_args = result.args
        self.assertEqual(len(exception_args), 1)
        # Exception "message" should include the trap name.
        self.assertIn('no-such-trap', exception_args[0])


    def test_task_catches_non_existing_trap_exception(self):

        def task():
            try:
                yield ('this-trap-does-not-exist',)
            except TrapDoesNotExist:
                yield ('sleep', 0)

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)


    def test_wrong_trap_arg_count_raises_exception(self):

        def task():
            yield ('sleep',)

        success, result = run(task)
        self.assertFalse(success)
        self.assertIsInstance(result, TrapArgCountWrong)
        exception_args = result.args
        self.assertEqual(len(exception_args), 1)
        # Exception "message" should include 'argument', somehow.
        self.assertIn('argument', exception_args[0])


    def test_task_catches_wrong_trap_arg_count_exception(self):

        def task():
            try:
                yield ('sleep', 1, 2, 3)
            except TrapArgCountWrong:
                yield ('sleep', 0)

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)


# ----------------------------------------------------------------------------
