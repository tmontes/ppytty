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


    async def handle_idle_next(self, **kw):

        await super().handle_idle_next()
        self._log.warning('%s: text=%r kw=%r', self, self._text, kw)
        return 'done'


    async def handle_cleanup(self, **kw):

        self._log.info('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup(**kw)


# ----------------------------------------------------------------------------
