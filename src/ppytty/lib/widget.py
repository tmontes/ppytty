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

    def __init__(self, id=None, geometry=None, color=None):

        super().__init__(id=id, initial_state='idle')

        self._geometry = geometry or visual.geometry_full()
        self._color = color or visual.color()
        self._window = None


    async def handle_idle_next(self, **hints):

        geometry = self._geometry
        if 'geometry' in hints:
            geometry.update(hints['geometry'])

        color = self._color
        if 'color' in hints:
            color.update(hints['color'])

        import random; color['bg'] = random.randint(1, 255)

        window = await api.window_create(**geometry, **color)
        # TODO: maybe avoid rendering now, let the sub-class do that?
        await api.window_render(window)
        self._log.debug('%s: created window: %r', self, window)
        self._window = window
        return 'done'


    async def handle_cleanup(self, **window_destroy_args):

        await api.window_destroy(self._window, **window_destroy_args)
        self._log.debug('%s: destroyed window %r', self, window_destroy_args)

        self.im_done()



# ----------------------------------------------------------------------------
