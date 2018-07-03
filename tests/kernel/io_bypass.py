# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import collections

from ppytty.kernel import hw

from unittest import TestCase, mock



class _FakeInputFile(object):

    def __init__(self, fd=0):

        self.fd = fd
        self.buffer = collections.deque()


    def fileno(self):

        return self.fd


    def feed_data(self, some_bytes):

        for i in range(len(some_bytes)):
            self.buffer.append(some_bytes[i:i+1])



class _AutoTimeFakeInputController(object):

    def __init__(self, fake_input=None):
        self._monotonic = 0
        self._fake_input = fake_input

    def time_monotonic(self):
        return self._monotonic

    def select_select(self, rlist, wlist, xlist, timeout=None):
        # timeout=None means forever, for now assume 42
        timeout = 42 if timeout is None else timeout
        self._monotonic += timeout
        if self._fake_input and self._fake_input.buffer:
            read_fds = (self._fake_input.fileno(),)
        else:
            read_fds = ()
        return read_fds, None, None

    def os_read(self, *args):
        return self._fake_input.buffer.popleft()

    def time_monotonic(self):
        return self._monotonic



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



class _NoOutputExtraPatchingTestCase(NoOutputTestCase):

    # Derived class objects must set self._patches before calling this setUp().

    def setUp(self):

        self._mock_patches = [mock.patch(w, new=r) for w, r in self._patches]
        for patch in self._mock_patches:
            patch.start()


    def tearDown(self):

        for patch in self._mock_patches:
            patch.stop()



class NoOutputAutoTimeTestCase(_NoOutputExtraPatchingTestCase):

    def setUp(self):

        self._auto_time = _AutoTimeFakeInputController()
        self._patches = [
            # Patch ppytty.kernel.hw output related attributes.
            ('ppytty.kernel.hw.time_monotonic', self._auto_time.time_monotonic),
            ('ppytty.kernel.hw.select_select', self._auto_time.select_select),
        ]
        super().setUp()


    @property
    def auto_time_monotonic(self):

        return self._auto_time._monotonic



class NoOutputAutoTimeControlledInputTestCase(_NoOutputExtraPatchingTestCase):

    def setUp(self):

        self.fake_stdin = _FakeInputFile(fd=0)
        self.input_control = _AutoTimeFakeInputController(self.fake_stdin)

        self._patches = [
            # Patch ppytty.kernel.hw output related attributes.
            ('ppytty.kernel.hw.sys_stdin', self.fake_stdin),
            ('ppytty.kernel.hw.time_monotonic', self.input_control.time_monotonic),
            ('ppytty.kernel.hw.select_select', self.input_control.select_select),
            ('ppytty.kernel.hw.os_read', self.input_control.os_read),
        ]
        super().setUp()


# ----------------------------------------------------------------------------
