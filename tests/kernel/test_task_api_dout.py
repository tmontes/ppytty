# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    def test_direct_print(self):

        os_write_mock = self.output_mocks['ppytty.kernel.hw.os_write']

        def task():
            # discard any previously emmited output
            os_write_mock.reset_mock()
            yield ('direct-print', 'this is the output message')
            # return a copy of all calls to our mocked os.write
            # (motive: on exiting, run outputs terminal escapes)
            return os_write_mock.call_args_list[:]

        success, os_write_mock_calls = run(task)
        self.assertTrue(success)

        # os.write was called at least once
        self.assertGreaterEqual(len(os_write_mock_calls), 1)

        # c[0] is the call args tuple; c[0][1] is the 2nd arg to os.write
        written_bytes = b''.join(c[0][1] for c in os_write_mock_calls)

        # `direct-print` will add a trailing b'\n'
        self.assertEqual(written_bytes, b'this is the output message\n')


# ----------------------------------------------------------------------------
