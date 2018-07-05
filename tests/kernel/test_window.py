# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

from ppytty.kernel import window

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    # Inheriting from NoOutputTestCase just for the bytes_match method.

    def setUp(self):

        self.WIDTH = 40
        self.HEIGHT = 15
        self.w = window.Window(0, 0, self.WIDTH, self.HEIGHT)
        self.sbt = window._SelfBlessingsTerminal


    def _assert_blank_window_rendered(self, rendered_bytes):

        blank_line = self.WIDTH * ' '
        expected = []
        expected.append(
            # First line: move to 0, 0 + normal text attributes + spaces.
            self.sbt.move(0, 0) + self.sbt.normal + blank_line
        )
        for line_number in range(1, 15):
            expected.append(
                # Each other line: move to line, 0 + spaces.
                self.sbt.move(line_number, 0) + blank_line
            )
        expected_bytes = ''.join(expected).encode('latin1')

        expected_suffixes = [
            # Trailing: normal text attributes + move to 0, 0.
            self.sbt.normal.encode('latin1'),
            self.sbt.move(0, 0).encode('latin1'),
        ]

        self.bytes_match(rendered_bytes, [], expected_suffixes, expected_bytes)


    def test_render(self):

        rendered_bytes = self.w.render()
        self._assert_blank_window_rendered(rendered_bytes)


    def test_rerender(self):

        _ = self.w.render()
        rendered_bytes = self.w.render()
        self.assertEqual(rendered_bytes, b'', 'no bytes produced on re-render')


    def test_rerender_full(self):

        _ = self.w.render()
        rendered_bytes = self.w.render(full=True)
        self._assert_blank_window_rendered(rendered_bytes)


    def test_clear_then_render(self):

        _ = self.w.render()

        # We already know this.
        rendered_bytes = self.w.render()
        self.assertEqual(rendered_bytes, b'', 'no bytes produced on re-render')

        # clear will force next render to output a fully blank window.
        self.w.clear()
        rendered_bytes = self.w.render()
        self._assert_blank_window_rendered(rendered_bytes)


    def test_print_then_render(self):

        _ = self.w.render()

        plain_text = 'text in window'
        self.w.print(plain_text)
        rendered_bytes = self.w.render()

        expected_prefixes = [
            # Cursor should be moved to top left and text attributes normal.
            self.sbt.move(0, 0).encode('latin1'),
            self.sbt.normal.encode('latin1'),
        ]

        # Payload is a full line of text, filled up with b' ' to the right.
        plain_text_bytes = plain_text.encode('UTF-8')
        remaining_spaces = b' ' * (self.WIDTH - len(plain_text))
        expected_bytes = plain_text_bytes + remaining_spaces

        expected_suffixes = [
            # Normal text attributes expected and curser right after plain_text.
            self.sbt.normal.encode('latin1'),
            self.sbt.move(0, len(plain_text)).encode('latin1'),
        ]
        self.bytes_match(rendered_bytes, expected_prefixes, expected_suffixes, expected_bytes)


    def test_print_positioned_then_render(self):

        _ = self.w.render()

        COLUMN, ROW = 4, 2

        plain_text = 'text in window'
        self.w.print(plain_text, x=COLUMN, y=ROW)
        rendered_bytes = self.w.render()

        expected_prefixes = [
            # Cursor should be moved row=2, col=0 + normal text attributes.
            self.sbt.move(ROW, 0).encode('latin1'),
            self.sbt.normal.encode('latin1'),
        ]

        # Payload is a full line of text, filled up with b' ' to the right.
        spaces_before = b' ' * COLUMN
        plain_text_bytes = plain_text.encode('UTF-8')
        spaces_after = b' ' * (self.WIDTH - len(plain_text) - COLUMN)
        expected_bytes = spaces_before + plain_text_bytes + spaces_after

        expected_suffixes = [
            # Normal text attributes expected and curser right after plain_text.
            self.sbt.normal.encode('latin1'),
            self.sbt.move(ROW, COLUMN+len(plain_text)).encode('latin1'),
        ]
        self.bytes_match(rendered_bytes, expected_prefixes, expected_suffixes, expected_bytes)


# ----------------------------------------------------------------------------
