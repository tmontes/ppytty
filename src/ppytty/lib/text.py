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


    async def handle_idle_next(self, slide_number, slide_count):

        await super().handle_idle_next()
        self._log.warning('%s: displayed text %r', self, self._text)
        return 'done'


    async def handle_cleanup(self, **_kwargs):

        self._log.warning('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup()


# ----------------------------------------------------------------------------
