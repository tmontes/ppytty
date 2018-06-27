# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from unittest import TestCase, mock



class NoOutputTestCase(TestCase):

    _PATCHES = [
        # Patch ppytty.kernel.hw output related attributes.
        ('ppytty.kernel.hw.os_write', mock.DEFAULT),
        ('ppytty.kernel.hw.termios_tcgetattr', mock.DEFAULT),
        ('ppytty.kernel.hw.termios_tcsetattr', mock.DEFAULT),
        ('ppytty.kernel.hw.sys_stdout', mock.DEFAULT),

        # Patch blessings usage of ioctl to return an 80x25 terminal size.
        # (it would otherwise fail when given the above mocked stdout)
        ('blessings.ioctl', b'\x19\x00P\x00\x00\x00\x00\x00'),
    ]

    @classmethod
    def setUpClass(cls):

        cls._mock_patches = [
            mock.patch(what, return_value=rv)
            for what, rv in cls._PATCHES
        ]

        for patch in cls._mock_patches:
            patch.start()



    @classmethod
    def tearDownClass(cls):

        for patch in cls._mock_patches:
            patch.stop()


# ----------------------------------------------------------------------------
