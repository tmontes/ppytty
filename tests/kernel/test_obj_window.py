# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest
import types

from ppytty.kernel import window

from . import helper_io



class TestNonRenderingAspects(unittest.TestCase):

    def setUp(self):

        self.sbt = window._SelfBlessingsTerminal
        self.parent = types.SimpleNamespace()
        self.parent.bt = self.sbt
        self.parent.width = 80
        self.parent.height = 25


    def test_sbt_too_large_fg_color(self):

        with self.assertRaises(ValueError):
            self.sbt.color(256)


    def test_sbt_too_large_bg_color(self):

        with self.assertRaises(ValueError):
            self.sbt.on_color(256)


    def test_window_overlaps(self):

        tests = [
            # self overlap
            [(0, 0, 80, 25), (0, 0, 80, 25), True,],
            # second inside first
            [(0, 0, 80, 25), (10, 5, 50, 15), True,],
            # side by side, touching
            [(0, 0, 40, 25), (40, 0, 40, 25), False,],
            # one on top of the other, touching
            [(0, 0, 80, 15), (0, 15, 80, 10), False,],
            # second top-left corner inside first
            [(0, 0, 40, 20), (20, 10, 40, 20), True,],
            # first bottom-right touching second top-left
            [(0, 0, 20, 10), (20, 10, 20, 10), False,],
        ]
        for w1args, w2args, expect_overlap in tests:
            with self.subTest(w1args=w1args, w2args=w2args, eo=expect_overlap):
                w1 = window.Window(self.parent, *w1args)
                w2 = window.Window(self.parent, *w2args)
                w1overlap = w1.overlaps(w2)
                w2overlap = w2.overlaps(w1)
                # The overlap operation is cummutative.
                self.assertEqual(w1overlap, w2overlap, 'overlap disagreement')
                # Does it match what we expect?
                self.assertEqual(expect_overlap, w1overlap, 'overlap')


    def test_window_geometry(self):

        tests = [
            # absolute geometry window
            (dict(x=4, y=2, w=40, h=10, dx=0, dy=0, dw=0, dh=0), (4, 2, 40, 10)),
            # absolute geometry window, with deltas
            (dict(x=4, y=2, w=40, h=10, dx=2, dy=1, dw=-2, dh=-1), (6, 3, 38, 9)),
            # full screen window
            (dict(x=0, y=0, w=1.0, h=1.0, dx=0, dy=0, dw=0, dh=0), (0, 0, 80, 25)),
            # full-screen window with 1 column/row margin
            (dict(x=0, y=0, w=1.0, h=1.0, dx=1, dy=1, dw=-2, dh=-2), (1, 1, 78, 23)),
            # full-left-hand side window
            (dict(x=0, y=0, w=0.5, h=1.0, dx=0, dy=0, dw=0, dh=0), (0, 0, 40, 25)),
            # full-right-hand side window
            (dict(x=0.5, y=0, w=0.5, h=1.0, dx=0, dy=0, dw=0, dh=0), (40, 0, 40, 25)),
            # 20 column width, right aligned window
            (dict(x=-20, y=0, w=20, h=1.0, dx=0, dy=0, dw=0, dh=0), (60, 0, 20, 25)),
            # 40% - 1 line height, bottom aligned window, shifted 1 line up
            (dict(x=0, y=-0.4, w=1.0, h=0.4, dx=0, dy=-1, dw=0, dh=-1), (0, 14, 80, 9)),
        ]
        for win_kwargs, expected_geometry in tests:
            with self.subTest(win_kwargs=win_kwargs):
                w = window.Window(self.parent, **win_kwargs)
                geometry = (w._left, w._top, w.width, w.height)
                self.assertEqual(geometry, expected_geometry, 'bad geometry')



class TestWithHiddenCursor(helper_io.NoOutputTestCase):

    # Inheriting from NoOutputTestCase just for the bytes_match method.

    def setUp(self):

        self.WIDTH = 40
        self.HEIGHT = 15
        self.sbt = window._SelfBlessingsTerminal
        parent = types.SimpleNamespace()
        parent.bt = self.sbt
        parent.width = 80
        parent.height = 25
        self.w = window.Window(parent, 0, 0, self.WIDTH, self.HEIGHT)


    def _assert_blank_window_rendered(self, rendered_bytes):

        blank_line = self.WIDTH * ' '
        expected = []
        expected.append(
            # First line: hide cursor + move to 0, 0 + normal text attributes + spaces.
            self.sbt.hide_cursor + self.sbt.move(0, 0) + self.sbt.normal + blank_line
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
            # Cursor should be hidden, moved to top left and text attributes normal.
            self.sbt.hide_cursor.encode('latin1'),
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
            # Cursor should be hidden + moved row=2, col=0 + normal text attributes.
            self.sbt.hide_cursor.encode('latin1'),
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


    def _assert_render_positioned_colored_print(self, column, row, fg, bg):

        _ = self.w.render()

        plain_text = 'text in window'
        self.w.print(plain_text, x=column, y=row, fg=fg, bg=bg)
        rendered_bytes = self.w.render()


        expected_prefixes = [
            # Cursor should be hiddent + moved row=2, col=0 + normal text attributes.
            self.sbt.hide_cursor.encode('latin1'),
            self.sbt.move(row, 0).encode('latin1'),
            self.sbt.normal.encode('latin1'),
        ]

        # Payload is a full line of text:
        expected = [
            # Spaces before
            ' ' * column,
            # Set formatting (always starts with normal)
            self.sbt.normal,
            self.sbt.color(fg),
            self.sbt.on_color(bg),
            plain_text,
            # Reset formatting
            self.sbt.normal,
            # Spaces after
            ' ' * (self.WIDTH - len(plain_text) - column),
        ]
        expected_bytes = ''.join(expected).encode('latin1')

        expected_suffixes = [
            # Normal text attributes expected and curser right after plain_text.
            self.sbt.normal.encode('latin1'),
            self.sbt.move(row, column+len(plain_text)).encode('latin1'),
        ]
        self.bytes_match(rendered_bytes, expected_prefixes, expected_suffixes, expected_bytes)


    def test_print_positioned_and_colored_then_render(self):

        positions_and_colors = [
            (4, 2, 254, 31),
            (2, 4, 7, 4),
            # These fg/gb vales were carefully selected as >=8 <5 with no
            # repeated RGB entries in pyte FG_BG_256 table.
            (7, 10, 8, 12),
        ]
        for column, row, fg, bg in positions_and_colors:
            with self.subTest(column=column, row=row, fg=fg, bg=bg):
                self._assert_render_positioned_colored_print(column, row, fg, bg)


# ----------------------------------------------------------------------------
