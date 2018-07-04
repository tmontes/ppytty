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
        self.os_write_mock = self.output_mocks['ppytty.kernel.hw.os_write']
        self.os_write_mock.reset_mock()


    def _get_written_bytes(self):

        # c[0] is the call args tuple; c[0][1] is the 2nd arg to os.write
        return b''.join(c[0][1] for c in self.os_write_mock.call_args_list)


    def _assert_full_80x25_spaces(self, output_bytes):

        # Strip possibly nested fake <tigetstr>/<tparm> calls and count b' '.
        # The test output terminal is 80x25 so we should get 2000.
        open_fake, close_fake, space = b'<> '
        depth = 0
        space_count = 0
        for byte_value in output_bytes:
            if byte_value == space and depth == 0:
                space_count += 1
            elif byte_value == open_fake:
                depth += 1
            elif byte_value == close_fake:
                depth -=1
        self.assertEqual(space_count, 2000, '# of spaces on terminal render')


    def test_render(self):

        self.t.render()
        written_bytes = self._get_written_bytes()
        self._assert_full_80x25_spaces(written_bytes)


    def test_render_rerender(self):

        self.t.render()
        self.os_write_mock.reset_mock()
        self.t.render()
        written_bytes = self._get_written_bytes()
        self.assertEqual(written_bytes, b'', 'no bytes written on re-render')


    def test_render_rerender_full(self):

        self.t.render()
        self.os_write_mock.reset_mock()
        self.t.render(full=True)
        written_bytes = self._get_written_bytes()
        self._assert_full_80x25_spaces(written_bytes)


# ----------------------------------------------------------------------------
