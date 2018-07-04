# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    # These tests are somewhat crazy and, effectively, going way over what
    # they should in the sense that they are also verifying the behavior of
    # the blessings package on which the output depends, including expecting
    # it to depend on curses. The odds of either changing are, I say, low;
    # that doesn't mean that these tests are testing things we can't control.

    def _drive_output_test(self, trap, prefixes, payload, suffixes):

        os_write_mock = self.output_mocks['ppytty.kernel.hw.os_write']

        def task():
            # Discard any previously emmited output.
            os_write_mock.reset_mock()
            yield trap
            # Return a copy of all calls to the mocked hw.os_write. Motive: on
            # stopping, run() outputs terminal "cleanup" escapes which end up
            # on the original mock.
            return os_write_mock.call_args_list[:]

        success, os_write_mock_calls = run(task)
        self.assertTrue(success)

        # os.write was called at least once
        self.assertGreaterEqual(len(os_write_mock_calls), 1)

        # c[0] is the call args tuple; c[0][1] is the 2nd arg to os.write
        written_bytes = b''.join(c[0][1] for c in os_write_mock_calls)

        for expected_prefix in prefixes:
            actual_prefix = written_bytes[:len(expected_prefix)]
            self.assertEqual(actual_prefix, expected_prefix, 'bad prefix')
            written_bytes = written_bytes[len(expected_prefix):]

        for expected_suffix in reversed(suffixes):
            actual_suffix = written_bytes[-len(expected_suffix):]
            self.assertEqual(expected_suffix, actual_suffix, 'bad suffix')
            written_bytes = written_bytes[:-len(expected_suffix)]

        self.assertEqual(payload, written_bytes, 'bad payload')


    def test_direct_print(self):

        trap = ('direct-print', 'this is the output message')

        out_prefixes = []
        out_suffixes = []
        # direct-print with no arguments appends a b'\n' to the output.
        out_payload = b'this is the output message\n'
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


    def test_direct_print_with_position(self):

        trap = ('direct-print', 'this is the output message', 4, 2)

        # Expect curses.tigetstr('cup'), then passed to curses.tparm(..., 2, 4)
        # to position the cusor; tparm args are (row, col), ours are (col, row).
        out_prefixes = [
            b'<fake_tparm(b"<fake_tigetstr(\'cup\',)>", 2, 4)>',
        ]
        out_suffixes = []
        out_payload = b'this is the output message'
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


    def test_direct_print_with_position_and_cursor_restore(self):

        trap = ('direct-print', 'this is the output message', 4, 2, True)

        # Expect curses.tigetstr('sc') prefix to save the cursor position,
        # followed by the same cursor positioning as in the previous test.
        out_prefixes = [
            b'<fake_tigetstr(\'sc\',)>',
            b'<fake_tparm(b"<fake_tigetstr(\'cup\',)>", 2, 4)>',
        ]
        # Expect curses.tigetstr('rc') suffix to restore the cursor position.
        out_suffixes = [
            b'<fake_tigetstr(\'rc\',)>',
        ]
        out_payload = b'this is the output message'
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


    def test_direct_clear(self):

        trap = ('direct-clear', )

        out_prefixes = []
        out_suffixes = []
        # Expect curses.tigetstr('clear') to clear the output terminal.
        out_payload =  b'<fake_tigetstr(\'clear\',)>'
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


# ----------------------------------------------------------------------------
