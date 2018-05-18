# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from .. import tasks


class SlideSequence(tasks.Serial):

    def __init__(self, slides, *, nav_task, **kw):

        super_arg_dict = {
            'nav_task': nav_task,
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

        nav = tasks.KeyboardAction(self.key_map, name='slide')
        super().__init__(slides, nav_task=nav, **kw)



class SlideSequenceTimed(SlideSequence):

    def __init__(self, slides, *, delay, **kw):

        nav = tasks.DelayReturn(seconds=delay, return_value='next', name='slide')
        super().__init__(slides, nav_task=nav, **kw)



class Slide(tasks.Parallel):

    def run(self):

        yield ('clear',)
        result = yield from super().run()
        return result



class WidgetSequence(tasks.Serial):

    def __init__(self, widgets, *, nav_task, **kw):

        super_arg_dict = {
            'nav_task': nav_task,
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

        nav = tasks.KeyboardAction(keymap=self.key_map, name='widget')
        super().__init__(widgets, nav_task=nav, **kw)



class WidgetSequenceTimed(WidgetSequence):

    def __init__(self, widgets, *, delay, post_keyboard=True, post_delay=0, **kw):

        if post_keyboard or post_delay:
            widgets = list(widgets)
        if post_keyboard:
            done = tasks.KeyboardAction(keymap=WidgetSequenceKeyboard.key_map, name='widget')
            widgets.append(done)
        if post_delay:
            delay_widget = tasks.DelayReturn(seconds=post_delay)
            widgets.append(delay_widget)
        nav = tasks.DelayReturn(seconds=delay, return_value='next', name='widget')
        super().__init__(widgets, nav_task=nav, **kw)


# ----------------------------------------------------------------------------