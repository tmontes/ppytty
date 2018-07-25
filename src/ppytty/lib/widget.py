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

        super().__init__(id=id)

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

        self._log.warning('%s: creating window', self)
        window = await api.window_create(**geometry, **color)
        # TODO: maybe avoid rendering now, let the sub-class do that?
        await api.window_render(window)
        self._window = window
        self._log.warning('%s: created window: %r', self, self._window)
        return 'done'


    async def handle_cleanup(self, **_kw):

        # TODO: destroy the window without forcing full terminal render
        #       unless I'm the last widget before "changing slides",
        #       (whatever that means, in this / the slide's context).
        self._log.info('%s: destroy window (in deferred mode)', self)
        return await super().handle_cleanup()



# ----------------------------------------------------------------------------
