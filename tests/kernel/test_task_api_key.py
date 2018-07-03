# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run

from . import io_bypass



class Test(io_bypass.NoOutputAutoTimeControlledInputTestCase):

    def test_read_key(self):

        def task():
            result = yield ('read-key', 100)
            return result

        self.input_control.feed_data(b'x')

        success, result = run(task)

        self.assertTrue(success)
        self.assertEqual(result, b'x')


# ----------------------------------------------------------------------------
