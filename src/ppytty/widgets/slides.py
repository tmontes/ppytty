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
        yield ('run-widgets', self._widgets)
        yield ('wait-widgets', self._widgets)


    def reset(self):

        super().reset()
        for widget in self._widgets:
            widget.reset()



class SlideDeck(widget.Widget):

    def __init__(self, slides, **kw):

        super().__init__(**kw)
        self._slides = slides


    def run(self):

        keymap = yield ('get-keymap',)

        index = 0
        index_max = len(self._slides) - 1

        while True:
            slide = self._slides[index]
            slide.reset()
            yield ('run-widgets', [slide])
            yield ('wait-widgets', [slide])
            while True:
                key = yield ('read-key',)
                if key == keymap['next']:
                    if index < index_max:
                        index += 1
                        break
                    else:
                        return 'next'
                elif key == keymap['prev']:
                    if index > 0:
                        index -= 1
                        break
                    else:
                        return 'prev'
                elif key == keymap['reload']:
                    break


# ----------------------------------------------------------------------------