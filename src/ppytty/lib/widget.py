# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import collections

from ppytty.kernel import api

from . import thing
from . import geometry as g



class Widget(thing.Thing):

    # Widgets have states and are controlled via messages sent to them.
    # - They start in the 'idle' state.
    # - They move forward when they get a 'next' message:
    #   - Returning 'running' if the Widget can handle more 'next' messages...
    #   - ...or 'done' if the Widget cannot.
    # - Widgets may respond to the 'next' message with interim messages acting
    #   as requests for the 'next' sender to complete particular actions.
    #   Such interim requests must, however, be completed by returning one of
    #   'running' or 'done', as commented above.
    # - Widgets cleanup and stop when they get a 'cleanup' message.
    #   - ...successful cleanup handlers should return None.

    def __init__(self, id=None):

        super().__init__(id=id, initial_state='idle')


    def __invert__(self):

        return WidgetsCleaner(self)


    def request(self, request, **request_args):

        return WidgetRequester(self, request, **request_args)


    async def handle_idle_next(self, **kw):

        return 'done'


    async def handle_cleanup(self, **kw):

        self.im_done()


    # ------------------------------------------------------------------------
    # To be used by others to launch me/move me forward/clean me up.

    async def message_send_wait(self, message, until=('running', 'done'), request_handler=None):

        async def send_wait_task():
            await api.message_send(self, message)
            while True:
                sender, response = await api.message_wait()
                if sender is not self:
                    self._log.warning('unexpected sender=%r response=%r', sender, response)
                if response in until:
                    break
                if request_handler:
                    await request_handler(response)
                else:
                    self._log.warning('ignored response from %r: %r', sender, response)
            return response

        # Send/wait message on a child task to avoid conflicts with possible
        # message sending/waiting the caller may be running; in particular, all
        # Widgets are Things, and Things run a core message waiting/sending loop.

        await api.task_spawn(send_wait_task)
        completed, success, result = await api.task_wait()

        if completed is not send_wait_task or not success:
            self._log.warning('%r: unexpected send_wait_task completion: '
                              'completed=%r success=%r result=%r', self,
                              completed, success, result)

        return result


    async def launch(self, till_done=False, request_handler=None, **kw):

        await api.task_spawn(self)
        message = ('next', kw)
        while True:
            reached_state = await self.message_send_wait(message, request_handler=request_handler)
            if not till_done or reached_state == 'done':
                break
        return reached_state


    async def forward(self, **kw):

        message = ('next', kw)
        reached_state = await self.message_send_wait(message)
        return reached_state


    async def cleanup(self, **kw):

        message = ('cleanup', kw)
        cleanup_response = await self.message_send_wait(message, until=(None,))
        if cleanup_response is not None:
            self._log.warning('%r: unexpected cleanup response: %r', self, cleanup_response)
        completed, _, _ = await api.task_wait()
        if completed is not self:
            self._log.warning('%r: unexpected child terminated: %r', self, completed)
        self.reset()




class WindowWidget(Widget):

    # WindowWidgets are Widgets with windows.
    # They have a slightly more rich life-cycle:
    # - When launched they create a window:
    #   - Geometry will be set by self, if any...
    #   - ...falling back to launch provided geometry info.
    #   - The window will be/not be rendered per launch provided info.
    #   - ...if rendered, render options are obtained from launch info.
    # - When cleaned up the window is destroyed:
    #   - ...the window destruction arguments are obtained from cleanup info.

    padding = 0

    def __init__(self, id=None, geometry=None, color=None, padding=None):

        super().__init__(id=id)

        self._geometry = geometry or {}
        # self._color = color or _color.default()

        # Clockwise, from top, inspired by CSS.
        self._pad_top = None
        self._pad_right = None
        self._pad_bottom = None
        self._pad_left = None
        self._set_padding(padding or self.padding)

        self._window = None


    def _set_padding(self, padding):

        if isinstance(padding, (tuple, list)):
            pad_count = len(padding)
            if pad_count == 4:
                self._pad_top, self._pad_right, self._pad_bottom, self._pad_left = padding
            elif pad_count == 2:
                pad_vertical, pad_horizontal = padding
                self._pad_top = self._pad_bottom = pad_vertical
                self._pad_right = self._pad_left = pad_horizontal
            else:
                raise ValueError(f'bad padding sequence length: {padding!r}')
        elif isinstance(padding, int):
            self._pad_top = self._pad_right = self._pad_bottom = self._pad_left = padding
        elif padding:
            raise ValueError(f'padding must be int or 2/4-tuple/list of ints: {padding!r}')


    @property
    def window(self):

        return self._window


    # Used when no valid geometry is available from context or self.
    _fallback_geometry = g.full()

    async def handle_idle_next(self, geometry=None, color=None, render=True,
                               terminal_render=True):

        await super().handle_idle_next()

        win_geometry = collections.ChainMap(
            self._geometry,
            geometry or {},
            self._fallback_geometry,
        )

        # win_color = self._color
        # if color:
        #     win_color.update(color)

        import random; win_color = dict(bg=random.randint(1, 255))

        self._window = await api.window_create(**win_geometry, **win_color)
        if render:
            await api.window_render(self._window, terminal_render=terminal_render)

        return 'done'


    async def handle_cleanup(self, **window_destroy_args):

        await api.window_destroy(self._window, **window_destroy_args)
        self._log.debug('%s: destroyed window %r', self, window_destroy_args)

        await super().handle_cleanup()


    # ------------------------------------------------------------------------
    # To be used by others to render me.

    async def render(self, render=True, **window_render_args):

        if render:
            await api.window_render(self._window, **window_render_args)



class WidgetsCleaner(Widget):

    """
    WidgetsCleaner class.

    Once 'next'ed asks the controller task to cleanup its wrapped/referenced
    widgets and becomes 'done'.
    """

    # Only the whoever launched the Widgets can properly clean them up: Widgets
    # are Tasks, their termination must be waited on by their parent.

    def __init__(self, *widgets):

        super().__init__()

        self._widgets = widgets


    def __repr__(self):

        return f'<{self.__class__.__name__} {self._widgets!r}>'


    async def handle_idle_next(self, terminal_render=True, clear_buffer=False,
                               **_kw):

        # When a Slide launches me I'll be passed several launch time arguments.
        # I don't need them, but must accept them; thus **_kw.

        await super().handle_idle_next()

        self._log.info('%r: asking controller to cleanup %r', self, self._widgets)
        window_destroy_args = dict(
            terminal_render=terminal_render,
            clear_buffer=clear_buffer,
        )
        await api.message_send(self.controller, ('cleanup', (self._widgets, window_destroy_args)))

        return 'done'



class WidgetsLauncher(Widget):

    """
    WidgetsLauncher class.

    Once 'next'ed asks the controller task to launch its wrapped/referenced
    widgets and becomes 'done'.
    """

    def __init__(self, *widgets):

        super().__init__()

        self._widgets = widgets


    def __repr__(self):

        return f'<{self.__class__.__name__} {self._widgets!r}>'


    async def handle_idle_next(self, **_kw):

        # When a Slide launches me I'll be passed several launch time arguments.
        # I don't need them, but must accept them; thus **_kw.

        await super().handle_idle_next()

        self._log.info('%r: asking controller to launch %r', self, self._widgets)
        await api.message_send(self.controller, ('launch', self._widgets))

        return 'done'



class WidgetRequester(Widget):

    """
    WidgetRequester class.

    Once 'next'ed asks the controller task to cleanup its wrapped/referenced
    widgets and becomes 'done'.
    """

    def __init__(self, widget, request, **request_args):

        super().__init__()

        self._widget = widget
        self._message = (request, request_args)


    def __repr__(self):

        return f'<{self.__class__.__name__} {self._widget!r} {self._message!r}>'


    async def handle_idle_next(self, **_kw):

        # When a Slide launches me I'll be passed several launch time arguments.
        # I don't need them, but must accept them; thus **_kw.

        await super().handle_idle_next()

        self._log.info('%r: asking controller to request %r from %r', self, self._message, self._widget)
        await api.message_send(self.controller, ('message', (self._widget, self._message)))

        return 'done'


# ----------------------------------------------------------------------------
