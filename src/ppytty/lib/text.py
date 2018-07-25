# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget



class Text(widget.Widget):

    def __init__(self, text=None, **kw):

        super().__init__()

        self._text = text


    async def handle_idle_next(self, **kw):

        await super().handle_idle_next()
        self._log.warning('%s: display text=%r kw=%r', self, self._text, kw)
        return 'done'


    async def handle_cleanup(self, **_kw):

        self._log.warning('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup()


# ----------------------------------------------------------------------------
