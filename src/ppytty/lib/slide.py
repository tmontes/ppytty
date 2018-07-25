# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget



class SlideTemplate(object):

    def __init__(self, widgets=None):

        self.widgets = widgets if widgets is not None else ()



class Slide(widget.Widget):

    def __init__(self, title, template=SlideTemplate(), widgets=None, **kw):

        super().__init__(id=title)

        self._template = template

        self._widgets = widgets if widgets is not None else ()
        self._widget_count = len(widgets)
        self._current_index = None


    def log_where(self, slide_number, slide_count):

        self._log.warning('%s: slide %r/%r at widget %r/%r', self,
                          slide_number, slide_count,
                          self._current_index+1, self._widget_count)


    async def handle_idle_next(self, **kw):

        await super().handle_idle_next()

        self._log.warning('%r: launching template widgets', self)
        for widget in self._template.widgets:
            await widget.launch(till_done=True, **kw)
        self._log.warning('%r: launched template widgets', self)

        self._current_index = 0
        self.log_where(kw.get('slide_number', '?'), kw.get('slide_count', '?'))
        if len(self._widgets) > 1:
            return 'ok'
        else:
            return 'done'


    async def handle_running_next(self, slide_number, slide_count):

        new_index = self._current_index + 1
        if new_index < self._widget_count:
            self._current_index = new_index
            self.log_where(slide_number, slide_count)
        if new_index < self._widget_count - 1:
            return 'ok'
        else:
            return 'done'


    async def handle_cleanup(self, **_kwargs):

        self._log.warning('%s: cleanup my widgets', self)

        self._log.warning('%r: cleaning up template widgets', self)
        for widget in self._template.widgets:
            await widget.cleanup()
        self._log.warning('%r: cleaned up template widgets', self)

        return await super().handle_cleanup()


# ----------------------------------------------------------------------------
