# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import serial



class Keymap(object):

    OUTER_PREV = b'{'
    OUTER_NEXT = b'}'
    OUTER_REDO = b'r'
    INNER_PREV = b'['
    INNER_NEXT = b']'
    INNER_REDO = b'r'



class KeyboardControlMixin(object):

    ACTION_MAP = {}

    def action_map(self, current_index, max_index):

        if current_index == 0:
            return getattr(self, 'ACTION_MAP_FIRST', self.ACTION_MAP)
        if current_index == max_index:
            return getattr(self, 'ACTION_MAP_LAST', self.ACTION_MAP)
        return self.ACTION_MAP



class OuterSequenceKeyboard(KeyboardControlMixin, serial.Serial):

    ACTION_MAP = {
        Keymap.OUTER_PREV: 'prev',
        Keymap.OUTER_NEXT: 'next',
        Keymap.OUTER_REDO: 'redo',
        Keymap.INNER_PREV: 'prev',
        Keymap.INNER_NEXT: 'next',
    }

    ACTION_MAP_FIRST = dict(ACTION_MAP)
    ACTION_MAP_FIRST[Keymap.OUTER_PREV] = 'redo'
    ACTION_MAP_FIRST[Keymap.INNER_PREV] = 'redo'

    ACTION_MAP_LAST = dict(ACTION_MAP)
    del ACTION_MAP_LAST[Keymap.OUTER_NEXT]
    del ACTION_MAP_LAST[Keymap.INNER_NEXT]

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



class InnerSequenceKeyboard(KeyboardControlMixin, serial.Serial):

    ACTION_MAP = {
        Keymap.OUTER_PREV: Keymap.OUTER_PREV,
        Keymap.OUTER_NEXT: Keymap.OUTER_NEXT,
        Keymap.INNER_PREV: Keymap.OUTER_REDO,
        Keymap.INNER_NEXT: 'next',
        Keymap.INNER_REDO: Keymap.OUTER_REDO,
    }

    ACTION_MAP_FIRST = dict(ACTION_MAP)
    ACTION_MAP_FIRST[Keymap.INNER_PREV] = Keymap.OUTER_PREV

    ACTION_MAP_LAST = dict(ACTION_MAP)
    ACTION_MAP_LAST[Keymap.INNER_NEXT] = Keymap.OUTER_NEXT

    def __init__(self, widgets, key_priority=100, **kw):

        mf = self.keyboard_monitor(self.action_map, key_priority, monitored_name=kw.get('name'))
        super().__init__(widgets, default_nav=None, monitor_factory=mf, **kw)



class InnerSequenceTimed(serial.Serial):

    def __init__(self, widgets, *, min_delay, max_delay, **kw):

        mf = self.time_monitor(min_delay, max_delay, monitored_name=kw.get('name'))
        super().__init__(widgets, default_nav=None, monitor_factory=mf, **kw)


# ----------------------------------------------------------------------------