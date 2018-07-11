# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import widget


class Label(widget.Widget):

    def __init__(self, text='', **kw):

        super().__init__(**kw)
        self._text = text


    async def run(self):

        await self.api.direct_print(self._text)


# ----------------------------------------------------------------------------
