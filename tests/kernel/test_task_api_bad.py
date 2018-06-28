# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run, TrapDoesNotExist

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    def test_non_existing_trap_raises_exception(self):

        def task():
            yield ('no-such-trap',)

        success, result = run(task)
        self.assertFalse(success)
        self.assertIsInstance(result, TrapDoesNotExist)


    def test_task_catches_non_existing_trap_exception(self):

        def task():
            try:
                yield ('this-trap-does-not-exist',)
            except TrapDoesNotExist:
                yield ('sleep', 0)

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)


# ----------------------------------------------------------------------------
