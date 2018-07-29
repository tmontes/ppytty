# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget
from . import geometry as g



class SlideTemplate(object):

    def __init__(self, widgets=None):

        self.widgets = widgets if widgets else ()


    def geometry(self, widget_index, widget_count):

        return None



class Slide(widget.WindowWidget):

    def __init__(self, title, template=SlideTemplate(), widgets=None,
                 geometry=None):

        geometry = geometry or g.full()
        super().__init__(id=title, geometry=geometry)

        self._title = title
        self._template = template

        self._widgets = widgets if widgets else ()
        self._widget_count = len(widgets)
        self._current_index = None
        self._current_widget = None

        # False if we can tell it to go 'next'. True otherwise.
        self._widget_done = None

        self._launched_widgets = []

        # See WidgetCleaner
        self._early_cleanup_widgets = []


    @property
    def at_last_widget(self):

        return self._current_index == self._widget_count-1


    async def handle_idle_next(self, **context):

        await super().handle_idle_next(render=False)

        context['slide_title'] = self._title

        self._log.info('%r: launching template widgets', self)
        for widget in self._template.widgets:
            await widget.launch(till_done=True, terminal_render=False, **context)
        self._log.info('%r: launched template widgets', self)

        if not self._widget_count:
            return 'done'

        self._current_index = 0
        self._current_widget = self._widgets[0]
        context['geometry'] = self._template.geometry(0, self._widget_count)
        widget_state = await self.launch_widget(terminal_render=False, **context)

        await self.render()

        return widget_state if self.at_last_widget else 'running'


    async def handle_running_next(self, **context):

        context['slide_title'] = self._title

        if self._widget_done:
            # launch next widget, if any
            new_index = self._current_index + 1
            if new_index < self._widget_count:
                self._current_index = new_index
                self._current_widget = self._widgets[new_index]
                context['geometry'] = self._template.geometry(new_index, self._widget_count)
                widget_state = await self.launch_widget(**context)
                return widget_state if self.at_last_widget else 'running'
            else:
                # last widget done, should have returned 'done' before
                self._log.warning('%s: should not be reached', self)
                return 'done'
        else:
            # move on with current widget
            widget_to_forward = self._current_widget
            self._log.info('%r: forwarding %r', self, widget_to_forward)
            widget_state = await widget_to_forward.forward(**context)
            self.update_navigation_from_response(widget_state)
            self._log.info('%r: forwarded %r done=%r', self, widget_to_forward, self._widget_done)
            return widget_state if self.at_last_widget else 'running'


    async def launch_widget(self, **context):

        widget_to_launch = self._current_widget

        self._log.info('%r: launching %r', self, widget_to_launch)
        widget_state = await widget_to_launch.launch(
            request_handler=self.launch_request_handler,
            **context,
        )
        self._launched_widgets.append(widget_to_launch)
        self.update_navigation_from_response(widget_state)
        self._log.info('%r: launched %r done=%r', self, widget_to_launch, self._widget_done)
        await self.cleanup_pending_widgets()
        return widget_state


    def update_navigation_from_response(self, response):

        self._widget_done = (response == 'done')
        if response not in ('running', 'done'):
            self._log.warning('%s: unexpected navigation response: %r', self, response)


    async def launch_request_handler(self, request):

        try:
            request, widget = request
            if request != 'cleanup':
                raise ValueError()
        except ValueError:
            self._log.warning('%s: invalid widget launch request: %r', self, request)
        else:
            self._early_cleanup_widgets.append(widget)


    async def cleanup_pending_widgets(self):

        while self._early_cleanup_widgets:
            widget = self._early_cleanup_widgets.pop()
            self._log.info('%r: runtime widget cleanup %r', self, widget)
            self._launched_widgets.remove(widget)
            await widget.cleanup()
            self._log.info('%r: runtime widget cleaned up %r', self, widget)


    async def handle_cleanup(self, **_kwargs):

        # Cleanup strategy:
        # - My widgets are cleaned up in such a way that their window
        #   destruction is not rendered to the output TTY.
        # - My window (inherited from Widget) is destroyed with clear_buffer
        #   activated as well; this means the output terminal's buffer is
        #   cleared but not rendered. It will be up to the next slide's window
        #   render to update the output TTY in one go.

        window_destroy_args = dict(terminal_render=False)

        self._log.info('%s: cleaning up widgets', self)
        while self._launched_widgets:
            widget = self._launched_widgets.pop()
            await widget.cleanup(**window_destroy_args)
        self._log.info('%s: cleaned up widgets', self)

        self._log.info('%r: cleaning up template widgets', self)
        for widget in self._template.widgets:
            await widget.cleanup(**window_destroy_args)
        self._log.info('%r: cleaned up template widgets', self)

        window_destroy_args['clear_buffer'] = True
        return await super().handle_cleanup(**window_destroy_args)


# ----------------------------------------------------------------------------
