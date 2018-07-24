# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget



class Slide(widget.Widget):

    def __init__(self, title, widgets, **kw):

        super().__init__(id=title)

        self._widgets = widgets
        self._current_index = None


    async def handle_idle_next(self, request):

        self._current_index = 0
        self._log.warning('%r: in-slide-nav to %r', self, self._current_index)
        if len(self._widgets) > 1:
            return 'ok'
        else:
            return 'done'


    async def handle_idle_prev(self, request):

        return 'done'


    async def handle_running_next(self, request):

        ni = self._current_index + 1
        if ni < len(self._widgets):
            self._current_index = ni
            self._log.warning('%r: in-slide-nav next to %r', self, self._current_index)
            return 'ok'
        else:
            self._log.warning('%r: in-slide-nav cannot go next', self)
            return 'done'


    async def handle_running_prev(self, request):

        ni = self._current_index - 1
        if ni >= 0:
            self._current_index = ni
            self._log.warning('%r: in-slide-nav prev to %r', self, self._current_index)
            return 'ok'
        else:
            self._log.warning('%r: in-slide-nav cannot go prev', self)
            return 'done'


# ----------------------------------------------------------------------------
