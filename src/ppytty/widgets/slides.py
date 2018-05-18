# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import utils


class SlideSequence(utils.Serial):

    def __init__(self, slides, *, nav_widget, **kw):

        super_arg_dict = {
            'nav_widget': nav_widget,
            'take_nav_hints': True,
            'give_nav_hints': False,
            'stop_over': False,
            'stop_under': False,
        }
        super().__init__(slides, **super_arg_dict, **kw)



class SlideSequenceKeyboard(SlideSequence):

    key_map = {
        b'{': 'prev',
        b'}': 'next',
        b'[': 'prev',
        b']': 'next',
        b'r': 'redo',
    }

    def __init__(self, slides, **kw):

        nav = utils.KeyboardAction(self.key_map, name='slide')
        super().__init__(slides, nav_widget=nav, **kw)



class SlideSequenceTimed(SlideSequence):

    def __init__(self, slides, *, delay, **kw):

        nav = utils.DelayReturn(seconds=delay, return_value='next', name='slide')
        super().__init__(slides, nav_widget=nav, **kw)



class Slide(utils.Parallel):

    def run(self):

        yield ('clear',)
        result = yield from super().run()
        return result



class WidgetSequence(utils.Serial):

    def __init__(self, widgets, *, nav_widget, **kw):

        super_arg_dict = {
            'nav_widget': nav_widget,
            'take_nav_hints': True,
            'give_nav_hints': True,
            'stop_over': True,
            'stop_under': True,
        }
        super().__init__(widgets, **super_arg_dict, **kw)



class WidgetSequenceKeyboard(WidgetSequence):

    key_map = {
        b'{': 'exit-prev',
        b'}': 'exit-next',
        b'[': 'exit-redo',
        b']': 'next',
        b'r': 'exit-redo',
    }

    def __init__(self, widgets, **kw):

        nav = utils.KeyboardAction(keymap=self.key_map, name='widget')
        super().__init__(widgets, nav_widget=nav, **kw)



class WidgetSequenceTimed(WidgetSequence):

    def __init__(self, widgets, *, delay, post_keyboard=True, post_delay=0, **kw):

        if post_keyboard or post_delay:
            widgets = list(widgets)
        if post_keyboard:
            done = utils.KeyboardAction(keymap=WidgetSequenceKeyboard.key_map, name='widget')
            widgets.append(done)
        if post_delay:
            delay_widget = utils.DelayReturn(seconds=post_delay)
            widgets.append(delay_widget)
        nav = utils.DelayReturn(seconds=delay, return_value='next', name='widget')
        super().__init__(widgets, nav_widget=nav, **kw)


# ----------------------------------------------------------------------------