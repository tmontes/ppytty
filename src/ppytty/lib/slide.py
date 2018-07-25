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

        self._title = title
        self._template = template

        self._widgets = widgets if widgets is not None else ()
        self._widget_count = len(widgets)
        self._current_index = None
        self._current_widget = None

        # False if we can tell it to go 'next'. True otherwise.
        self._widget_done = None

        self._launched_widgets = []


    @property
    def at_last_widget(self):

        return self._current_index == self._widget_count-1


    async def handle_idle_next(self, **context):

        await super().handle_idle_next()

        context['slide_title'] = self._title

        self._log.info('%r: launching template widgets', self)
        for widget in self._template.widgets:
            await widget.launch(till_done=True, **context)
        self._log.info('%r: launched template widgets', self)

        if not self._widget_count:
            return 'done'

        self._current_index = 0
        self._current_widget = self._widgets[0]
        launch_response = await self.launch_widget(**context)

        return launch_response if self.at_last_widget else 'ok'


    async def handle_running_next(self, **context):

        context['slide_title'] = self._title

        if self._widget_done:
            # launch next widget, if any
            new_index = self._current_index + 1
            if new_index < self._widget_count:
                self._current_index = new_index
                self._current_widget = self._widgets[new_index]
                launch_response = await self.launch_widget(**context)
                return launch_response if self.at_last_widget else 'ok'
            else:
                # last widget done, should have returned 'done' before
                self._log.warning('%s: should not be reached', self)
                return 'done'
        else:
            # move on with current widget
            destination = self._current_widget
            message = ('next', context)
            await api.message_send(destination, message)
            sender, response = await api.message_wait()
            if sender is not destination:
                # TODO: will the Thing message_wait loop mess with this?
                self._log.warning('%r: unexpected sender=%r response=%r', self, sender, response)
            self.update_navigation_from_response(response)
            return response if self.at_last_widget else 'ok'


    async def launch_widget(self, **context):

        widget_to_launch = self._current_widget

        self._log.info('%r: launching %r', self, widget_to_launch)
        response = await widget_to_launch.launch(till_done=False, **context)
        self._launched_widgets.append(widget_to_launch)
        self.update_navigation_from_response(response)
        self._log.info('%r: launched %r done=%r', self, widget_to_launch, self._widget_done)
        return response


    def update_navigation_from_response(self, response):

        self._widget_done = (response == 'done')
        if response not in ('ok', 'done'):
            self._log.warning('%s: unexpected navigation response: %r', self, response)


    async def handle_cleanup(self, **_kwargs):

        self._log.info('%s: cleaning up widgets', self)
        while self._launched_widgets:
            widget = self._launched_widgets.pop()
            await widget.cleanup()
        self._log.info('%s: cleaned up widgets', self)

        self._log.info('%r: cleaning up template widgets', self)
        for widget in self._template.widgets:
            await widget.cleanup()
        self._log.info('%r: cleaned up template widgets', self)

        return await super().handle_cleanup()


# ----------------------------------------------------------------------------
