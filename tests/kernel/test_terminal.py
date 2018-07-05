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


# ----------------------------------------------------------------------------
