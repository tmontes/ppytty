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
            yield ('run-task', widget)
            running_widgets.append(widget)
        while running_widgets:
            widget, return_action = yield ('wait-task',)
            running_widgets.remove(widget)

        if len(self._widgets) == 1:
            return return_action


    def reset(self):

        super().reset()
        for widget in self._widgets:
            widget.reset()



class Serial(widget.Widget):

    _ACTIONS = ['next', 'prev', 'redo', 'exit-next', 'exit-prev', 'exit-redo']

    def __init__(self, widgets, *, nav_widget=None,
                 take_nav_hints=True, give_nav_hints=True,
                 stop_over=True, stop_under=True, **kw):

        super().__init__(**kw)
        self._widgets = widgets
        self._nav_widget = nav_widget
        self._take_nav_hints = take_nav_hints
        self._give_nav_hints = give_nav_hints
        self._stop_over = stop_over
        self._stop_under = stop_under


    def run(self):

        index = 0
        index_max = len(self._widgets) - 1

        while True:
            widget = self._widgets[index]
            widget.reset()
            yield ('run-task', widget)
            _, nav_hint = yield ('wait-task',)
            action = 'next'
            if self._take_nav_hints:
                if nav_hint in self._ACTIONS:
                    action = nav_hint
                else:
                    action = None
            while True:
                if self._nav_widget and action is None:
                    self._nav_widget.reset()
                    yield ('run-task', self._nav_widget)
                    _, action = yield ('wait-task',)
                    if action not in self._ACTIONS:
                        self._log.warning('invalid nav_widget action %r', action)
                        action = None
                        continue
                if action == 'next':
                    if index < index_max:
                        index += 1
                        break
                    elif self._stop_over:
                        return action if self._give_nav_hints else None
                    else:
                        action = None
                        continue
                elif action == 'prev':
                    if index > 0:
                        index -= 1
                        break
                    elif self._stop_under:
                        return action if self._give_nav_hints else None
                    else:
                        action = None
                        continue
                elif action == 'redo':
                    break
                elif action and action.startswith('exit-') and self._give_nav_hints:
                    return action[5:]



class DelayReturn(widget.Widget):

    def __init__(self, *, seconds=0, return_value=None, **kw):

        super().__init__(**kw)
        self._seconds = seconds
        self._return_value = return_value


    def run(self):

        yield ('sleep', self._seconds)
        return self._return_value



class KeyboardAction(widget.Widget):

    def __init__(self, keymap, default_action=None, **kw):

        super().__init__(**kw)
        self._keymap = keymap
        self._default_action = default_action


    def run(self):

        key = yield ('read-key',)
        return self._keymap.get(key, self._default_action)


# ----------------------------------------------------------------------------
