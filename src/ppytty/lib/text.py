# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget



class Text(widget.Widget):

    def __init__(self, text, id=None, geometry=None, color=None):

        super().__init__(id=id, geometry=geometry, color=color)

        self._text = text


    async def handle_idle_next(self, geometry=None, color=None, render=True,
                               terminal_render=True, **context):

        await super().handle_idle_next(geometry=geometry, color=color, render=False)
        self._log.warning('%s: text=%r context=%r', self, self._text, context)
        await self.render(render=render, terminal_render=terminal_render)
        return 'done'


    async def handle_cleanup(self, **window_destroy_args):

        self._log.info('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup(**window_destroy_args)


# ----------------------------------------------------------------------------
