# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import types

from ppytty.kernel import api

from . import widget



class Bullets(widget.WindowWidget):

    def __init__(self, items, bullets='- ', space_h=None, space_v=0,
                 at_once=False, id=None, template_slot=None, geometry=None,
                 color=None):

        """
        Bullets

        `items`:    list/tuple of items; each item must be either a string,
                    representing a single bullet item, or a list/tuple of items,
                    representing sub-items.
        `bullets`:  string/callable.
        `space_h`:  None or int.
        `space_v`:  int.
        `at_once`:  bool.

        Arguments other than `items` support being passed a list/tuple to
        indicate the appropriate value for the given hierarchy level; example,
        passing ('*', '-') in `bullets` will use '*' to represent top-level
        bullets and '-' for the second (and remaining) levels.
        """

        super().__init__(id=id, template_slot=template_slot, geometry=geometry,
                         color=color)

        self._items = items
        self._depth = self._tree_depth(items)

        self._bullets = self._per_level_values('bullets', bullets, (str, types.FunctionType))
        self._at_once = self._per_level_values('at_once', at_once, bool)

        self._steps = self._compute_steps(items, self._at_once[0])
        self._log.debug('%r: steps=%r', self, self._steps)

        self._step_count = len(self._steps)
        self._current_step_index = None

        self._current_y = None


    def _tree_depth(self, items):

        if isinstance(items, (list, tuple)):
            if not items:
                raise ValueError('Unsupported empty items in Bullets.')
            else:
                return 1 + max(self._tree_depth(i) for i in items)
        elif isinstance(items, str):
            return 0
        else:
            raise ValueError(f'Unsupported value in Bullets items: {items!r}')


    def _per_level_values(self, name, value, types):

        if isinstance(value, types):
            return [value] * self._depth
        elif isinstance(value, (list, tuple)):
            if any(not isinstance(v, types) for v in value):
                raise ValueError(f'Unsupported bullets {name} values: {value!r}')
            result = value[:self._depth]
            while len(result) < self._depth:
                result.append(result[-1])
            return result
        else:
            raise ValueError(f'Unsupported Bullets {name} value: {value!r}')


    def _compute_steps(self, items, at_once, level=0):

        # Returns a list of steps where each step is a list of (level, text)
        # tuples to be displayed; computed based on the items hierarchy and
        # the respective level's at_once. If a given level's at_once is True,
        # all sub level's at_once are forced to True as well.

        steps = []
        if at_once:
            single_step = []
            for item in items:
                if isinstance(item, (list, tuple)):
                    sub_level = level+1
                    if not self._at_once[sub_level]:
                        self._log.warning('%r: Ignored level %r at_once=False', self, sub_level)
                    sub_steps = self._compute_steps(item, at_once, sub_level)
                    single_step.extend(sub_steps[0])
                else:
                    single_step.append((level, item))
            steps.append(single_step)
        else:
            for item in items:
                if isinstance(item, (list, tuple)):
                    sub_level = level+1
                    at_once = self._at_once[sub_level]
                    sub_steps = self._compute_steps(item, at_once, sub_level)
                    steps.extend(sub_steps)
                else:
                    steps.append([(level, item)])

        return steps


    @property
    def at_last_step(self):

        return self._current_step_index == self._step_count - 1


    def paint_window_contents(self, window, step=None):

        if step is None:
            # TODO: Need to clear and repaint up to self._current_step_index.
            self._log.warning('%r: no step to paint', self)
            return

        available_height = window.height - self._pad_top - self._pad_bottom

        for level, text in step:
            bullet = self._bullets[level]
            window.print(bullet + text, x=self._pad_left, y=self._current_y)
            self._current_y += 1
            available_height -= 1


    async def handle_idle_next(self, template_slot_callable=None, render=True,
                               terminal_render=True, **context):

        await super().handle_idle_next(template_slot_callable=template_slot_callable, render=False)

        self._current_y = self._pad_top
        self._current_step_index = 0

        self.paint_window_contents(self.window, self._steps[0])
        self.window.add_resize_callback(self.paint_window_contents)

        await self.render(render=render, terminal_render=terminal_render)
        return 'done' if self.at_last_step else 'running'


    async def handle_running_next(self, terminal_render=True, **context):

        new_index = self._current_step_index + 1
        if new_index < self._step_count:
            self._current_step_index = new_index
            self.paint_window_contents(self.window, self._steps[new_index])
            await self.render(terminal_render=terminal_render)
            return 'done' if self.at_last_step else 'running'
        else:
            return 'done'


    async def handle_cleanup(self, **window_destroy_args):

        self._log.info('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup(**window_destroy_args)


# ----------------------------------------------------------------------------
