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
        self._widget_count = len(widgets)
        self._current_index = None


    def log_where(self, slide_index, slide_count):

        self._log.warning('%s: slide %r/%r at widget %r/%r', self,
                          slide_index+1, slide_count,
                          self._current_index+1, self._widget_count)


    async def handle_idle_next(self, slide_index, slide_count):

        self._current_index = 0
        self.log_where(slide_index, slide_count)
        if len(self._widgets) > 1:
            return 'ok'
        else:
            return 'done'


    async def handle_running_next(self, slide_index, slide_count):

        new_index = self._current_index + 1
        if new_index < self._widget_count:
            self._current_index = new_index
            self.log_where(slide_index, slide_count)
        if new_index < self._widget_count - 1:
            return 'ok'
        else:
            return 'done'


    async def handle_cleanup(self, *_args):

        self._log.warning('%s: cleaning up', self)

        # TODO: clean up my widgets, when I have them.

        return await super().handle_cleanup()


# ----------------------------------------------------------------------------
