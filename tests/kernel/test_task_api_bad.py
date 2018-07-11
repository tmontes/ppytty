# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty.kernel import run, api
from ppytty.kernel.exceptions import TrapDoesNotExist, TrapArgCountWrong

from . import helper_io



class Test(helper_io.NoOutputTestCase):

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
                pass

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)


    def test_wrong_trap_arg_count_raises_exception(self):

        def task():
            yield (api.Trap.SLEEP,)

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
                yield (api.Trap.SLEEP, 1, 2, 3)
            except TrapArgCountWrong:
                pass

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)


# ----------------------------------------------------------------------------
