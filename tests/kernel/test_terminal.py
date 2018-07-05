# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

from ppytty.kernel import terminal

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    def setUp(self):

        self.t = terminal.Terminal()
        self.reset_os_written_bytes()


    def test_render(self):

        self.t.render()
        written_bytes = self.get_os_written_bytes()
        payload_bytes = self.strip_fake_curses_entries(written_bytes)
        self.assertEqual(payload_bytes, 80 * 25 * b' ')


    def _discard_first_render(self):

        self.t.render()
        self.reset_os_written_bytes()


    def test_rerender(self):

        self._discard_first_render()

        self.t.render()
        written_bytes = self.get_os_written_bytes()
        self.assertEqual(written_bytes, b'', 'no bytes written on re-render')


    def test_rerender_full(self):

        self._discard_first_render()

        self.t.render(full=True)
        written_bytes = self.get_os_written_bytes()
        payload_bytes = self.strip_fake_curses_entries(written_bytes)
        self.assertEqual(payload_bytes, 80 * 25 * b' ')


    def test_feed_text_then_render(self):

        self._discard_first_render()

        plain_text = b'this is the terminal'
        self.t.feed(plain_text)
        self.t.render()
        written_bytes = self.get_os_written_bytes()

        # The byte sequence used to position the cursor.
        tigetstr_cup = self.fake_tigetstr('cup')

        # Should start by positioning the cursor at (col=0, row=0).
        prefix = self.fake_tparm(tigetstr_cup, 0, 0)
        self.assertTrue(written_bytes.startswith(prefix), 'wrong prefix')

        # Should end by positioning the cursor at (col=len(plain_text), row=0).
        suffix = self.fake_tparm(tigetstr_cup, 0, len(plain_text))
        self.assertTrue(written_bytes.endswith(suffix), 'wrong suffix')

        # Payload should be a full line (plain_text is shorter than that): the
        # test terminal is 80 column wide, so the payload should start with the
        # plan_text and be filled with spaces.
        payload = self.strip_fake_curses_entries(written_bytes)
        expected = plain_text + b' ' * (80 - len(plain_text))
        self.assertEqual(payload, expected)


# ----------------------------------------------------------------------------
