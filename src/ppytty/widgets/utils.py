# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import widget


class Parallel(widget.Widget):

    def __init__(self, widgets, **kw):

        super().__init__(**kw)
        self._widgets = widgets


    def run(self):

        running_widgets = []

        for widget in self._widgets:
            yield ('run-widget', widget)
            running_widgets.append(widget)
        while running_widgets:
            widget, return_action = yield ('wait-widget',)
            running_widgets.remove(widget)

        if len(self._widgets) == 1:
            return return_action


    def reset(self):

        super().reset()
        for widget in self._widgets:
            widget.reset()



class Serial(widget.Widget):

    DEFAULT_ACTIONS = {
        'next': 'next',
        'prev': 'prev',
        'redo': 'redo',
    }

    def __init__(self, widgets, post_widget=None, action_map=None, **kw):

        super().__init__(**kw)
        self._widgets = widgets
        self._post_widget = post_widget
        self._action_map = action_map if action_map else self.DEFAULT_ACTIONS


    def run(self):

        index = 0
        index_max = len(self._widgets) - 1

        while True:
            widget = self._widgets[index]
            widget.reset()
            yield ('run-widget', widget)
            return_widget, return_action = yield ('wait-widget',)
            action = 'next'
            while True:
                if self._post_widget:
                    self._post_widget.reset()
                    yield ('run-widget', self._post_widget)
                    post_widget, post_return = yield ('wait-widget',)
                    action = self._action_map.get(post_return)
                if action == 'next':
                    if index < index_max:
                        index += 1
                        break
                    else:
                        return action
                elif action == 'prev':
                    if index > 0:
                        index -= 1
                        break
                    else:
                        return action
                elif movement == 'reload':
                    action



class Delay(widget.Widget):

    def __init__(self, seconds, **kw):

        super().__init__(**kw)
        self._seconds = seconds


    def run(self):

        yield ('sleep', self._seconds)



class KeyboardAction(widget.Widget):

    def __init__(self, keymap, default_action=None):

        super().__init__()
        self._keymap = keymap
        self._default_action = default_action

    def run(self):

       key = yield ('read-key',)
       return self._keymap.get(key, self._default_action)


# ----------------------------------------------------------------------------