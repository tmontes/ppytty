# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import serial



class OuterSequenceKeyboard(serial.Serial):

    action_map = {
        b'{': 'prev',
        b'}': 'next',
        b'[': 'prev',
        b']': 'next',
        b'r': 'redo',
    }

    def __init__(self, slides, key_priority=1000, **kw):

        mf = self.keyboard_monitor(self.action_map, key_priority, monitored_name=kw.get('name'))
        super().__init__(slides, default_nav=None, return_nav_hint=False,
                        stop_when_under=False, stop_when_over=False,
                        monitor_factory=mf, **kw)



class OuterSequenceTimed(serial.Serial):

    def __init__(self, slides, *, min_delay, max_delay, **kw):

        mf = self.time_monitor(min_delay, max_delay, monitored_name=kw.get('name'))
        super().__init__(slides, default_nav=None, return_nav_hint=False,
                        stop_when_under=False, stop_when_over=False,
                        monitor_factory=mf, **kw)



class InnerSequenceKeyboard(serial.Serial):

    action_map = {
        b'{': b'{',
        b'}': b'}',
        b'[': b'r',
        b']': 'next',
        b'r': b'r',
    }

    def __init__(self, widgets, key_priority=100, **kw):

        mf = self.keyboard_monitor(self.action_map, key_priority, monitored_name=kw.get('name'))
        super().__init__(widgets, default_nav=None, monitor_factory=mf, **kw)



class InnerSequenceTimed(serial.Serial):

    def __init__(self, widgets, *, min_delay, max_delay, **kw):

        mf = self.time_monitor(min_delay, max_delay, monitored_name=kw.get('name'))
        super().__init__(widgets, default_nav=None, monitor_factory=mf, **kw)


# ----------------------------------------------------------------------------