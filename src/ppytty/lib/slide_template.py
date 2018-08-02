# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import collections
import logging



log = logging.getLogger(__name__)



class SlideTemplate(object):

    widgets = ()
    widget_slots = ()

    def __init__(self, id=None, widgets=None, widget_slots=None):

        self._id = id
        self.widgets = widgets or self.widgets
        self.widget_slots = widget_slots or self.widget_slots

        if not all(w.geometry for w in self.widgets):
            raise ValueError(f'{self} widgets with no geometry.')

        if not isinstance(self.widget_slots, dict):
            self.widget_slots = {
                i: ws for i, ws in enumerate(self.widget_slots)
            }

        self._available_widget_slots = None
        self._slide = None


    def __repr__(self):

        me = repr(self._id) if self._id else hex(id(self))
        return f'<{self.__class__.__name__} {me}>'


    def initialize(self, slide):

        slot_delta = slide.no_geometry_widget_count - len(self.widget_slots)
        if slot_delta > 0:
            raise ValueError(f'{slot_delta} widgets with no geometry in {slide!r} '
                             f'for the existing widget slots in {self!r}')

        self._slide = slide
        self._available_widget_slots = collections.deque(self.widget_slots)


    def next_widget_slot(self, slot_name=None):

        slot = None

        if slot_name is None:
            if self._available_widget_slots:
                slot_name = self._available_widget_slots.popleft()
                slot = self.widget_slots[slot_name]
            else:
                log.error('%r: exauhsted template widget slots', self._slide)
        elif slot_name not in self.widget_slots:
            log.error('%r: no %r template widget slot', self._slide, slot_name)
        else:
            slot = self.widget_slots[slot_name]
            self._available_widget_slots.remove(slot_name)

        return slot


# ----------------------------------------------------------------------------
