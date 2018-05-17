# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import utils


class SlideDeck(utils.Serial):

    key_map = {
        b'{': 'prev',
        b'}': 'next',
        b'[': 'prev',
        b']': 'next',
        b'r': 'redo',
    }

    def __init__(self, slides, **kw):

        super_arg_dict = {
            'nav_widget': utils.KeyboardAction(keymap=self.key_map),
            'take_nav_hints': True,
            'give_nav_hints': False,
            'stop_over': False,
            'stop_under': False,
            **kw,
        }
        super().__init__(slides, **super_arg_dict)



class Slide(utils.Parallel):

    def run(self):

        yield ('clear',)
        result = yield from super().run()
        return result



class SlideContentSequence(utils.Serial):

    key_map = {
        b'{': 'exit-prev',
        b'}': 'exit-next',
        b'[': 'exit-redo',
        b']': 'next',
        b'r': 'exit-redo',
    }

    def __init__(self, widgets, *, nav_widget=None, **kw):

        if nav_widget is None:
            nav_widget = utils.KeyboardAction(keymap=self.key_map)

        super_arg_dict = {
            'nav_widget': nav_widget,
            'take_nav_hints': True,
            'give_nav_hints': True,
            'stop_over': True,
            'stop_under': True,
            **kw,
        }
        super().__init__(widgets, **super_arg_dict)


# ----------------------------------------------------------------------------