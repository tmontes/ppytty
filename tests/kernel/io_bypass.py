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
        self.monotonic = 0
        self.fake_input = fake_input

    def time_monotonic(self):
        return self.monotonic

    def select_select(self, rlist, wlist, xlist, timeout=None):
        # timeout=None means forever, for now assume 42
        timeout = 42 if timeout is None else timeout
        self.monotonic += timeout
        if self.fake_input and self.fake_input.buffer:
            read_fds = (self.fake_input.fileno(),)
        else:
            read_fds = ()
        return read_fds, None, None

    def os_read(self, *args):
        return self.fake_input.buffer.popleft()

    def feed_data(self, some_bytes):
        self.fake_input.feed_data(some_bytes)

    @property
    def buffer(self):
        return self.fake_input.buffer



class _Fake_tigetstr(object):

    def __init__(self, *args):
        self._args = args

    def decode(self, *_args):
        return f'<fake_tigetstr{self._args}>'



class _Fake_tparm(object):

    def __init__(self, *args):
        self._args = args

    def decode(self, *_args):
        return f'<fake_tparm{self._args}>'



class NoOutputTestCase(TestCase):

    _PATCHES = [
        # Patch ppytty.kernel.hw output related attributes.
        ('ppytty.kernel.hw.os_write', None, mock.DEFAULT),
        ('ppytty.kernel.hw.termios_tcgetattr', None, mock.DEFAULT),
        ('ppytty.kernel.hw.termios_tcsetattr', None, mock.DEFAULT),
        ('ppytty.kernel.hw.sys_stdout', None, mock.DEFAULT),

        # Patch blessings usage of ioctl to return an 80x25 terminal size.
        # (it would otherwise fail when given the above mocked stdout)
        ('blessings.ioctl', None, b'\x19\x00P\x00\x00\x00\x00\x00'),

        ('blessings.setupterm', None, mock.DEFAULT),
        ('blessings.tigetstr', _Fake_tigetstr, None),
        ('blessings.tparm', _Fake_tparm, None),
    ]

    @classmethod
    def setUpClass(cls):

        cls._output_mock_patches = {}
        for what, new_value, ret_value in cls._PATCHES:
            kwargs = {}
            if new_value is not None:
                kwargs['new'] = new_value
            if ret_value is not None:
                kwargs['return_value'] = ret_value
            patch = mock.patch(what, **kwargs)
            cls._output_mock_patches[what] = patch
            # what: mock.patch(what, return_value=rv) for what, rv in cls._PATCHES

        cls.output_mocks = {
            what: patch.start()
            for what, patch in cls._output_mock_patches.items()
        }

        cls._os_write_mock = cls.output_mocks['ppytty.kernel.hw.os_write']
        cls._tigetstr_mock = cls.output_mocks['blessings.tigetstr']
        cls._tparm_mock = cls.output_mocks['blessings.tparm']


    def reset_os_written_bytes(self):

        self._os_write_mock.reset_mock()


    def get_os_written_bytes(self):

        return b''.join(
            call[0][1] for call in self._os_write_mock.call_args_list
        )


    def fake_tigetstr(self, *args):

        return self._tigetstr_mock(*args).decode().encode('latin1')


    def fake_tparm(self, *args):

        return self._tparm_mock(*args).decode().encode('latin1')


    def bytes_match(self, bytes_, prefixes, suffixes, payload, strict=True):

        for expected_prefix in prefixes:
            actual_prefix = bytes_[:len(expected_prefix)]
            self.assertEqual(actual_prefix, expected_prefix, 'bad prefix')
            bytes_ = bytes_[len(expected_prefix):]

        for expected_suffix in reversed(suffixes):
            actual_suffix = bytes_[-len(expected_suffix):]
            self.assertEqual(expected_suffix, actual_suffix, 'bad suffix')
            bytes_ = bytes_[:-len(expected_suffix)]

        if not strict:
            bytes_ = self.strip_fake_curses_entries(bytes_)

        self.assertEqual(payload, bytes_, 'bad payload')


    @staticmethod
    def strip_fake_curses_entries(byte_string):

        open_fake, close_fake = b'<>'
        depth = 0
        result_bytes = []
        for byte_value in byte_string:
            if byte_value == open_fake:
                depth += 1
            elif byte_value == close_fake:
                depth -= 1
            elif depth == 0:
                result_bytes.append(byte_value)
        return bytes(result_bytes)


    @classmethod
    def tearDownClass(cls):

        for patch in cls._output_mock_patches.values():
            patch.stop()



class _ExtraPatchingMixin(object):

    # Mixed classes must set self._patches before calling this setUp().

    def setUp(self):

        self._extra_mock_patches = {
            what: mock.patch(what, new=nv) for what, nv in self._patches
        }
        self.extra_mocks = {
            what: patch.start()
            for what, patch in self._extra_mock_patches.items()
        }


    def tearDown(self):

        for patch in self._extra_mock_patches.values():
            patch.stop()



class NoOutputAutoTimeTestCase(_ExtraPatchingMixin, NoOutputTestCase):

    def setUp(self):

        self.auto_time = _AutoTimeFakeInputController()
        self._patches = [
            # Patch ppytty.kernel.hw output related attributes.
            ('ppytty.kernel.hw.time_monotonic', self.auto_time.time_monotonic),
            ('ppytty.kernel.hw.select_select', self.auto_time.select_select),
        ]
        super().setUp()



class NoOutputAutoTimeControlledInputTestCase(_ExtraPatchingMixin, NoOutputTestCase):

    def setUp(self):

        fake_stdin = _FakeInputFile(fd=0)
        self.input_control = _AutoTimeFakeInputController(fake_stdin)

        self._patches = [
            # Patch ppytty.kernel.hw output related attributes.
            ('ppytty.kernel.hw.sys_stdin', fake_stdin),
            ('ppytty.kernel.hw.time_monotonic', self.input_control.time_monotonic),
            ('ppytty.kernel.hw.select_select', self.input_control.select_select),
            ('ppytty.kernel.hw.os_read', self.input_control.os_read),
        ]
        super().setUp()


# ----------------------------------------------------------------------------
