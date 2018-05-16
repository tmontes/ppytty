# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import widget


class Slide(widget.Widget):

    def __init__(self, widgets, **kw):

        super().__init__(**kw)
        self._widgets = widgets


    def run(self):

        yield ('clear',)
        yield ('create-widgets', self._widgets)
        yield ('wait-widgets', self._widgets)



class SlideDeck(widget.Widget):

    def __init__(self, slides, **kw):

        super().__init__(**kw)
        self._slides = slides


    def run(self):

        for slide in self._slides:
            yield ('create-widgets', [slide])
            yield ('wait-widgets', [slide])
            key = yield ('read-key',)


# ----------------------------------------------------------------------------