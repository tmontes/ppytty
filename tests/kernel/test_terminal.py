# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

from ppytty.kernel import terminal

# For an explanation of what _SlefBlessingsTerminal is, refer to its comment.
from ppytty.kernel.window import _SelfBlessingsTerminal as sbt

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

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


# ----------------------------------------------------------------------------
