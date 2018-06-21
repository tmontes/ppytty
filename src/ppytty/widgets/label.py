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


    def run(self):

        yield ('direct-print', self._text)


# ----------------------------------------------------------------------------
