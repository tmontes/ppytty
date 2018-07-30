# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import collections
import functools

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

        self._widget_steps = []
        self._widget_step_count = 0
        self._widget_count = 0
        self._init_widget_steps(widgets or ())

        self._current_step_index = None
        self._current_widget_step = None

        # False if self._current_widget_step accepts 'next'; True otherwise.
        self._widget_step_done = None

        # Tracks template Widget slots, consumed (increased) as Widgets are
        # launched.
        self._template_slot_index = None

        self._template_geometry = functools.partial(self._template.geometry,
                                                    widget_count=self._widget_count)

        self._launched_widgets = []

        # See WidgetCleaner / WidgetGroup
        self._widget_launchtime_requests = collections.defaultdict(list)


    def _init_widget_steps(self, widgets_arg):

        for w in widgets_arg:
            if isinstance(w, (list, tuple)):
                for sub_w in w:
                    if not isinstance(sub_w, widget.Widget):
                        raise ValueError(f'{sub_w!r} in {w!r} must be a Widget')
                    if isinstance(sub_w, widget.WidgetsLauncher):
                        raise ValueError(f'unsupported {sub_w!r} in {w!r}')
                    if not isinstance(sub_w, widget.WidgetsCleaner):
                        self._widget_count += 1
                self._widget_steps.append(widget.WidgetsLauncher(*w))
                continue
            elif not isinstance(w, widget.Widget):
                raise ValueError(f'{w!r} must be a Widget')
            elif isinstance(w, widget.WidgetsLauncher):
                raise ValueError(f'use a list/tuple instead of {w!r}')
            elif not isinstance(w, widget.WidgetsCleaner):
                self._widget_count += 1
            self._widget_steps.append(w)

        self._widget_step_count = len(self._widget_steps)


    @property
    def at_last_step(self):

        return self._current_step_index == self._widget_step_count-1


    async def handle_idle_next(self, **context):

        await super().handle_idle_next(render=False)

        context['slide_title'] = self._title

        self._log.info('%r: launching template widgets', self)
        for widget in self._template.widgets:
            await widget.launch(till_done=True, terminal_render=False, **context)
        self._log.info('%r: launched template widgets', self)

        if not self._widget_count:
            return 'done'

        self._current_step_index = 0
        self._current_widget_step = self._widget_steps[0]
        self._template_slot_index = 0
        context['geometry'] = self._template_geometry(self._template_slot_index)
        widget_state = await self.launch_widget(terminal_render=False, **context)

        await self.render()

        return widget_state if self.at_last_step else 'running'


    async def handle_running_next(self, **context):

        context['slide_title'] = self._title

        if self._widget_step_done:
            # launch next widget, if any
            new_step = self._current_step_index + 1
            if new_step < self._widget_step_count:
                self._current_step_index = new_step
                self._current_widget_step = self._widget_steps[new_step]
                self._template_slot_index += 1
                context['geometry'] = self._template_geometry(self._template_slot_index)
                widget_state = await self.launch_widget(**context)
                return widget_state if self.at_last_step else 'running'
            else:
                # last widget done, should have returned 'done' before
                self._log.warning('%s: should not be reached', self)
                return 'done'
        else:
            # move on with current widget
            widget_to_forward = self._current_widget_step
            self._log.info('%r: forwarding %r', self, widget_to_forward)
            widget_state = await widget_to_forward.forward(**context)
            self.update_navigation_from_response(widget_state)
            self._log.info('%r: forwarded %r done=%r', self, widget_to_forward, self._widget_step_done)
            return widget_state if self.at_last_step else 'running'


    async def launch_widget(self, widget=None, **context):

        widget_to_launch = widget or self._current_widget_step

        self._log.info('%r: launching %r', self, widget_to_launch)
        widget_state = await widget_to_launch.launch(
            request_handler=functools.partial(self.launch_request_handler, widget_to_launch),
            **context,
        )
        self._launched_widgets.append(widget_to_launch)
        self.update_navigation_from_response(widget_state)
        self._log.info('%r: launched %r done=%r', self, widget_to_launch, self._widget_step_done)
        await self.complete_launchtime_requests(widget_to_launch, **context)
        return widget_state


    def update_navigation_from_response(self, response):

        self._widget_step_done = (response == 'done')
        if response not in ('running', 'done'):
            self._log.warning('%s: unexpected navigation response: %r', self, response)


    async def launch_request_handler(self, widget, request):

        self._widget_launchtime_requests[widget].append(request)


    async def complete_launchtime_requests(self, requester_widget, **context):

        widget_launchtime_requests = self._widget_launchtime_requests[requester_widget]

        while widget_launchtime_requests:
            request = widget_launchtime_requests.pop()
            try:
                action, action_args = request
            except ValueError:
                self._log.warning('%r: invalid %r launch time request: %r', self, requester_widget, request)
                continue
            if action == 'launch':
                for widget_to_launch in action_args:
                    context['geometry'] = self._template_geometry(self._template_slot_index)
                    self._template_slot_index += 1
                    await self.launch_widget(widget=widget_to_launch, till_done=True, **context)
                self._template_slot_index -= 1
            elif action == 'cleanup':
                for widget_to_cleanup in action_args:
                    if widget_to_cleanup not in self._launched_widgets:
                        self._log.warning('%r: cannot cleanup unlaunched widget %r', self, widget_to_cleanup)
                        continue
                    self._launched_widgets.remove(widget_to_cleanup)
                    await widget_to_cleanup.cleanup()
            else:
                self._log.warning('%r: invalid %r launch time action: %r', self, requester_widget, action)

        del self._widget_launchtime_requests[requester_widget]


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
