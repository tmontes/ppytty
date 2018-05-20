# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import serial



class OuterSequenceKeyboard(serial.Serial):

    key_map = {
        b'{': 'prev',
        b'}': 'next',
        b'[': 'prev',
        b']': 'next',
        b'r': 'redo',
    }

    def __init__(self, slides, **kw):

        super().__init__(slides, default_nav=None, return_nav_hint=False,
                        stop_when_under=False, stop_when_over=False,
                        monitor_factory=self.keyboard_monitor(self.key_map), **kw)



class OuterSequenceTimed(serial.Serial):

    def __init__(self, slides, *, delay, **kw):

        super().__init__(slides, default_nav=None, return_nav_hint=False,
                        stop_when_under=False, stop_when_over=False,
                        monitor_factory=self.timed_monitor(delay), **kw)



class InnerSequenceKeyboard(serial.Serial):

    key_map = {
        b'{': 'exit-prev',
        b'}': 'exit-next',
        b'[': 'exit-redo',
        b']': 'next',
        b'r': 'exit-redo',
    }

    def __init__(self, widgets, **kw):

        mf = self.keyboard_monitor(self.key_map)
        super().__init__(widgets, default_nav=None, monitor_factory=mf, **kw)



class InnerSequenceTimed(serial.Serial):

    def __init__(self, widgets, *, delay, **kw):

        mf = self.timed_monitor(delay)
        super().__init__(widgets, default_nav=None, monitor_factory=mf, **kw)


# ----------------------------------------------------------------------------