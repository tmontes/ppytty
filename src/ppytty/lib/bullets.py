# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import textwrap

from ppytty.kernel import api

from . import widget



_BULLET_PROVIDER_METHODS = []

def _bullet_provider(method):

    _BULLET_PROVIDER_METHODS.append(method)
    return method



class Bullets(widget.WindowWidget):

    @staticmethod
    @_bullet_provider
    def numbers(start=1, fmt='d', prefix='', suffix='. '):

        return lambda n: f'{prefix}{n + start:{fmt}}{suffix}'


    @staticmethod
    @_bullet_provider
    def letters(start='a', fmt='s', prefix='', suffix='. '):

        return lambda n: prefix + format(chr(n + ord(start)), fmt) + suffix


    def __init__(self, items, bullets='- ', truncate_with='... ', spacing=0,
                 at_once=False, id=None, template_slot=None, geometry=None,
                 color=None, padding=None):

        """
        Bullets

        `items`:    list/tuple of items; each item must be either a string,
                    representing a single bullet item, or a list/tuple of items,
                    representing sub-items.
        `bullets`:  string/callable.
        `spacing`:  int.
        `at_once`:  bool.

        Arguments other than `items` support being passed a list/tuple to
        indicate the appropriate value for the given hierarchy level; example,
        passing ('*', '-') in `bullets` will use '*' to represent top-level
        bullets and '-' for the second (and remaining) levels.
        """

        super().__init__(id=id, template_slot=template_slot, geometry=geometry,
                         color=color, padding=padding)

        self._items = items
        self._depth = self._tree_depth(items)

        self._bullets = self._per_level_bullets(bullets)
        self._truncate_with = truncate_with
        self._truncate_width_len = len(truncate_with)
        self._spacing = self._per_level_spacing(spacing)
        self._at_once = self._per_level_at_once(at_once)

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


    def _per_level_values(self, name, value, valid_value):

        if valid_value(value):
            return [value] * self._depth
        elif isinstance(value, (list, tuple)):
            if any(not valid_value(v) for v in value):
                raise ValueError(f'Unsupported bullets {name} values: {value!r}')
            result = value[:self._depth]
            while len(result) < self._depth:
                result.append(result[-1])
            return result
        else:
            raise ValueError(f'Unsupported Bullets {name} value: {value!r}')


    def _per_level_bullets(self, bullets):

        valid_value = lambda v: isinstance(v, str) or callable(v)
        return self._per_level_values('bullets', bullets, valid_value)

    def _per_level_spacing(self, spacing):

        valid_value = lambda v: isinstance(v, int)
        return self._per_level_values('spacing', spacing, valid_value)


    def _per_level_at_once(self, at_once):

        valid_value = lambda v: isinstance(v, bool)
        return self._per_level_values('at_once', at_once, valid_value)


    def _compute_steps(self, items, at_once, left_pad=0, level=0):

        # Returns a list of steps where each is a list of (bullet, text, spacing)
        # tuples to be displayed; computed based on the items hierarchy and
        # the respective level's at_once. If a given level's at_once is True,
        # all sub level's at_once are forced to True as well.

        def level_bullets():
            level_bullet = self._bullets[level]
            if level_bullet in _BULLET_PROVIDER_METHODS:
                # Methods themselves passed as bullets; need to call them.
                level_bullet = level_bullet()
            bullets = []
            bullets_width = 0
            item_number = 0
            for item in items:
                if isinstance(item, (list, tuple)):
                    continue
                bullet = level_bullet(item_number) if callable(level_bullet) else level_bullet
                item_number += 1
                bullets_width = max(bullets_width, len(bullet))
                bullets.append(bullet)
            return iter(bullets), bullets_width

        steps = []
        bullets_iter, bullets_width = level_bullets()
        spacing = self._spacing[level]
        if at_once:
            single_step = []
            for item in items:
                if isinstance(item, (list, tuple)):
                    sub_level = level+1
                    if not self._at_once[sub_level]:
                        self._log.warning('%r: Ignored level %r at_once=False', self, sub_level)
                    sub_steps = self._compute_steps(item, at_once, left_pad+bullets_width, sub_level)
                    if single_step and sub_steps and sub_steps[0][-1][-1] > spacing:
                        # Previous outer level spacing too short: fix it.
                        single_step[-1][-1] = sub_steps[0][-1][-1]
                    single_step.extend(sub_steps[0])
                else:
                    if single_step and single_step[-1][-1] < spacing:
                        # Previous inner level spacing too short: fix it.
                        single_step[-1][-1] = spacing
                    the_bullet = next(bullets_iter)
                    left_fill = ' '*(left_pad + bullets_width - len(the_bullet))
                    single_step.append([left_fill + the_bullet, item, spacing])
            steps.append(single_step)
        else:
            for item in items:
                if isinstance(item, (list, tuple)):
                    sub_level = level+1
                    at_once = self._at_once[sub_level]
                    sub_steps = self._compute_steps(item, at_once, left_pad+bullets_width, sub_level)
                    if steps and sub_steps and sub_steps[0][-1][-1] > spacing:
                        # Previous outer level spacing too short: fix it.
                        steps[-1][-1][-1] = sub_steps[0][-1][-1]
                    steps.extend(sub_steps)
                else:
                    if steps and steps[-1][-1][-1] < spacing:
                        # Previous inner level spacing too short: fix it.
                        steps[-1][-1][-1] = spacing
                    the_bullet = next(bullets_iter)
                    left_fill = ' '*(left_pad + bullets_width - len(the_bullet))
                    steps.append([[left_fill + the_bullet, item, spacing]])

        return steps


    @property
    def at_last_step(self):

        return self._current_step_index == self._step_count - 1


    def _step_lines(self, step, available_width):

        for bullet, text, spacing in step:
            lines = textwrap.wrap(text, width=available_width-len(bullet))
            last_line_number = len(lines) - 1
            for line_number, line in enumerate(lines):
                line_spacing = spacing if line_number == last_line_number else 0
                yield line_number, bullet, line, line_spacing


    def paint_window_contents(self, window, step=None):

        if step is None:
            # TODO: Need to clear and repaint up to self._current_step_index.
            self._log.warning('%r: no step to paint', self)
            return

        available_width = window.width - self._pad_left - self._pad_right
        available_height = window.height - self._current_y - self._pad_bottom

        for line_number, bullet, line, spacing in self._step_lines(step, available_width):
            if available_height <= 0:
                if self._truncate_width_len > available_width:
                    line = self._truncate_with[:available_width]
                else:
                    line = self._truncate_with * (available_width // self._truncate_width_len)
                window.print(line, x=self._pad_left, y=window.height-self._pad_bottom-1)
                break
            prefix = ' ' * len(bullet) if line_number else bullet
            window.print(prefix + line, x=self._pad_left, y=self._current_y)
            delta_y = 1 + spacing
            self._current_y += delta_y
            available_height -= delta_y


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
