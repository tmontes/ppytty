# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

from ppytty.kernel import terminal

# For an explanation of what _SlefBlessingsTerminal is, refer to its comment.
from ppytty.kernel.window import _SelfBlessingsTerminal as sbt

from . import helper_io



class Test(helper_io.NoOutputTestCase):

    # Much like the direct-output trap tests, these tests are checking the
    # behaviour of more things than the actual terminal itself. In particular
    # they verify the actual bytes sent to os.write which, with the current
    # terminal implementation, end up exercising (and verifying) the wrapped
    # pyte.Screen/ByteStream implementations.
    #
    # This makes the tests slower (and maybe more fragile) but also helps
    # making sure that the terminal actually produces correct output.

    def setUp(self):

        self.t = terminal.Terminal()
        self.reset_os_written_bytes()


    def _assert_blank_terminal_rendered(self, written_bytes):

        prefixes = [
            self.fake_tparm(self.fake_tigetstr('cup'), 0, 0),
        ]
        payload = b' ' * 80 * 25
        self.bytes_match(written_bytes, prefixes, [], payload, strict=False)


    def test_render(self):

        self.t.render()
        written_bytes = self.get_os_written_bytes()
        self._assert_blank_terminal_rendered(written_bytes)


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
        self._assert_blank_terminal_rendered(written_bytes)


    def test_feed_text_then_render(self):

        self._discard_first_render()

        plain_text = b'this is the terminal'
        self.t.feed(plain_text)
        self.t.render()
        written_bytes = self.get_os_written_bytes()

        prefixes = [
            # Start by positioning the cursor at (col=0, row=0).
            self.fake_tparm(self.fake_tigetstr('cup'), 0, 0),
        ]
        suffixes = [
            # End by positioning the cursor at (col=len(plain_text), row=0).
            self.fake_tparm(self.fake_tigetstr('cup'), 0, len(plain_text)),
        ]
        # Payload should be a full line (plain_text is shorter than that): the
        # test terminal is 80 column wide, so the payload should start with the
        # plain_text and be filled with spaces.
        payload = plain_text + b' ' * (80 - len(plain_text))

        # Non-strict means: accept that after validating prefixs and suffixes,
        # the remaining bytes may contain additional fake tigetstr/tparm parts.
        self.bytes_match(written_bytes, prefixes, suffixes, payload, strict=False)


    def test_feed_positioned_text_then_render(self):

        self._discard_first_render()

        COLUMN, ROW = 4, 2
        plain_text = b'positioned text'
        data_to_feed = b''.join([
            sbt.move(ROW, COLUMN).encode('latin1'),
            plain_text,
        ])
        self.t.feed(data_to_feed)
        self.t.render()
        written_bytes = self.get_os_written_bytes()

        # render should output the full 80 column terminal row.
        prefixes = [
            # Start by positioning the cursor at (col=0, row=2).
            self.fake_tparm(self.fake_tigetstr('cup'), ROW, 0),
        ]
        suffixes = [
            # End by positioning the cursor to the right of plain_text.
            self.fake_tparm(self.fake_tigetstr('cup'), ROW, COLUMN+len(plain_text)),
        ]
        # Payload should be a full line (plain_text is shorter than that): the
        # test terminal is 80 column wide, so the payload should start with
        # COLUMN x b' ', then plain_text, then filled to the end with b' '.
        spaces_before = b' ' * COLUMN
        spaces_after = b' ' * (80 - len(plain_text) - COLUMN)
        payload = spaces_before + plain_text + spaces_after

        # Non-strict means: accept that after validating prefixs and suffixes,
        # the remaining bytes may contain additional fake tigetstr/tparm parts.
        self.bytes_match(written_bytes, prefixes, suffixes, payload, strict=False)


    def test_clear_then_render(self):

        self._discard_first_render()

        # Incremental rendering with not output produces no bytes.
        self.t.render()
        written_bytes = self.get_os_written_bytes()
        self.assertEqual(written_bytes, b'', 'no bytes written on re-render')

        # clear will force next render to output a fully blank terminal.
        self.t.clear()
        self.t.render()
        written_bytes = self.get_os_written_bytes()

        self._assert_blank_terminal_rendered(written_bytes)


# ----------------------------------------------------------------------------
