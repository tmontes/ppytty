# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import thing
from . import visual



class Widget(thing.Thing):

    # Widget have states and are controlled via messages sent to them.
    # - They start in the 'idle' state.
    # - They move forward when they get a 'next' message:
    #   - ...returning 'running' if they can handle more "next" messages.
    #   - ...or 'done' when they cannot.
    # - They should cleanup and stop when they get a 'cleanup' message.
    #   - ...successful cleanup handlers should return None.

    def __init__(self, id=None, geometry=None, color=None):

        super().__init__(id=id, initial_state='idle')

        self._geometry = geometry or visual.geometry_full()
        self._color = color or visual.color()
        self._window = None


    @property
    def window(self):

        return self._window


    async def handle_idle_next(self, geometry=None, color=None, render=True,
                               terminal_render=True):

        win_geometry = self._geometry
        if geometry:
            win_geometry.update(geometry)

        win_color = self._color
        if color:
            win_color.update(color)

        import random; win_color['bg'] = random.randint(1, 255)

        self._window = await api.window_create(**win_geometry, **win_color)
        if render:
            await api.window_render(self._window, terminal_render=terminal_render)

        return 'done'


    async def handle_cleanup(self, **window_destroy_args):

        await api.window_destroy(self._window, **window_destroy_args)
        self._log.debug('%s: destroyed window %r', self, window_destroy_args)

        self.im_done()


    # ------------------------------------------------------------------------
    # To be used by others to launch me/render me/clean me up.

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


    async def render(self, render=True, **window_render_args):

        if render:
            await api.window_render(self._window, **window_render_args)


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

        self._log.warning('%s: unexpected sender=%r response=%r', self, sender, response)


# ----------------------------------------------------------------------------
