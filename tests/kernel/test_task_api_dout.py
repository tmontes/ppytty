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

        def task():
            # Discard any previously emmited output.
            self.reset_os_written_bytes()
            yield trap
            # Return written bytes now. Motive: on stopping, run() outputs
            # terminal "cleanup" escapes which end up as written bytes.
            return self.get_os_written_bytes()

        success, written_bytes = run(task)
        self.assertTrue(success)

        self.bytes_match(written_bytes, prefixes, suffixes, payload, strict=True)


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
            self.fake_tparm(self.fake_tigetstr('cup'), 2, 4),
        ]
        out_suffixes = []
        out_payload = b'this is the output message'
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


    def test_direct_print_with_position_and_cursor_restore(self):

        trap = ('direct-print', 'this is the output message', 4, 2, True)

        # Expect curses.tigetstr('sc') prefix to save the cursor position,
        # followed by the same cursor positioning as in the previous test.
        out_prefixes = [
            self.fake_tigetstr('sc'),
            self.fake_tparm(self.fake_tigetstr('cup'), 2, 4),
        ]
        # Expect curses.tigetstr('rc') suffix to restore the cursor position.
        out_suffixes = [
            self.fake_tigetstr('rc'),
        ]
        out_payload = b'this is the output message'
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


    def test_direct_clear(self):

        trap = ('direct-clear', )

        out_prefixes = []
        out_suffixes = []
        # Expect curses.tigetstr('clear') to clear the output terminal.
        out_payload = self.fake_tigetstr('clear')
        self._drive_output_test(trap, out_prefixes, out_payload, out_suffixes)


# ----------------------------------------------------------------------------
