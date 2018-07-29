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
    #   - ...returning 'running' if they can handle more "next" messages.
    #   - ...or 'done' when they cannot.
    # - They should cleanup and stop when they get a 'cleanup' message.
    #   - ...successful cleanup handlers should return None.

    def __init__(self, id=None):

        super().__init__(id=id, initial_state='idle')


    async def handle_idle_next(self, **kw):

        return 'done'


    async def handle_cleanup(self, **kw):

        self.im_done()


    # ------------------------------------------------------------------------
    # To be used by others to launch me/move me forward/clean me up.

    async def launch(self, till_done=False, **kw):

        await api.task_spawn(self)
        message = ('next', kw)
        done = False
        while not done:
            await api.message_send(self, message)
            sender, reached_state = await api.message_wait()
            if sender is not self:
                self.log_unexpected_sender(sender, reached_state)
            if not till_done or reached_state == 'done':
                done = True
        return reached_state


    async def forward(self, **kw):

        message = ('next', kw)
        await api.message_send(self, message)
        sender, reached_state = await api.message_wait()
        if sender is not self:
            self.log_unexpected_sender(sender, reached_state)
        return reached_state


    async def cleanup(self, **kw):

        message = ('cleanup', kw)
        await api.message_send(self, message)
        sender, cleanup_response = await api.message_wait()
        if sender is not self:
            self.log_unexpected_sender(sender, cleanup_response)
        if cleanup_response is not None:
            self._log.warning('%r: unexpected cleanup response: %r', self, cleanup_response)
        completed, _, _ = await api.task_wait()
        if completed is not self:
            self._log.warning('%r: unexpected child terminated: %r', self, completed)
        self.reset()


    def log_unexpected_sender(self, sender, response):

        self._log.warning('%r: unexpected sender=%r response=%r', self, sender, response)




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

    def __init__(self, id=None, geometry=None, color=None, padding=None):

        super().__init__(id=id)

        self._geometry = geometry or {}
        # self._color = color or _color.default()

        # Clockwise, from top, inspired by CSS.
        self._pad_top = 0
        self._pad_right = 0
        self._pad_bottom = 0
        self._pad_left = 0
        self._set_padding(padding)

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



class WidgetCleaner(Widget):

    """
    WidgetCleaner class.

    Wraps a Widget and has a very simple life-cycle: once 'next'ed, it cleans
    up the wrapped Widget and is 'done'. On cleanup, it tries to cleanup the
    wrapped Widget if it hasn't been cleaned up yet.
    """

    def __init__(self, widget, id=None):

        super().__init__(id=id)

        self._widget = widget


    async def handle_idle_next(self, **kw):

        await super().handle_idle_next()

        self._log.warning('%r: handle_idle_next, ignoring kw=%r', self, kw)

        # TODO

        # Cannot cleanup self._widget myself, otherwise I'll hang waiting
        # for child termination when self._widget, that successfully terminates,
        # is not my child!!!

        # Solution: Must somehow tell the slide to do that.
        # - Can we message the parent?... (probably not, needs thinking)
        # - How can we return something indicating please cleanup self._widget?
        #   (whatever we return will be processed by our driver but, up to now
        #   all we can return the simple 'done', 'running' strings...)

        # This needs thought!

        return 'cleanup-widget'


    async def handle_cleanup(self, **kw):

        # TODO: Is this needed?
        self._log.warning('%r: handle_cleanup (nothing to do?), ignoring kw=%r', self, kw)
        return await self.handle_cleanup()


# ----------------------------------------------------------------------------
