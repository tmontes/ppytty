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

        if not isinstance(self.widget_slots, dict):
            self.widget_slots = {
                i: ws for i, ws in enumerate(self.widget_slots)
            }

        self._referenced_slot_names = None
        self._available_slot_names = None
        self._slide = None


    def __repr__(self):

        me = repr(self._id) if self._id else hex(id(self))
        return f'<{self.__class__.__name__} {me}>'


    def validate(self, slide):

        # Template widgets must have geometry.

        if not all(w.geometry for w in self.widgets):
            raise ValueError(f'{self} widgets with no geometry.')

        # All slide.windowed_widgets must referece valid slots, if any.

        self._referenced_slot_names = {
            w.template_slot for w in slide.windowed_widgets if w.template_slot
        }

        invalid_wslot_names = self._referenced_slot_names - self.widget_slots.keys()
        if invalid_wslot_names:
            raise ValueError(f'Widgets in {slide!r} reference non-existing '
                             f'template slots: {", ".join(invalid_wslot_names)}')

        # There are enough widget_slots for all slide.windowed_widgets not
        # referencing template slots and not having geometry.

        no_geometry_widgets = [
            w for w in slide.windowed_widgets
            if not w.template_slot and not w.geometry
        ]
        slot_delta = len(no_geometry_widgets) - len(self.widget_slots)
        if slot_delta > 0:
            raise ValueError(f'{slot_delta} widgets with no geometry in {slide!r} '
                             f'for the existing widget slots in {self!r}')

        self._slide = slide


    def reset_widget_slots(self):

        # Set the available slots to all unreferenced ones.

        self._available_slot_names = collections.deque(
            slot_name for slot_name in self.widget_slots
            if slot_name not in self._referenced_slot_names
        )


    def next_widget_slot(self, slot_name=None):

        slot = None

        if slot_name is None:
            if self._available_slot_names:
                slot_name = self._available_slot_names.popleft()
                slot = self.widget_slots[slot_name]
            else:
                log.error('%r: exauhsted template widget slots', self._slide)
        elif slot_name not in self.widget_slots:
            log.error('%r: no %r template widget slot', self._slide, slot_name)
        else:
            slot = self.widget_slots[slot_name]

        return slot


# ----------------------------------------------------------------------------
