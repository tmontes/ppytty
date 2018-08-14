# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import enum
import functools
import textwrap

from ppytty.kernel import api

from . import widget



class Text(widget.WindowWidget):

    class Align(enum.Enum):

        LEFT = enum.auto()
        CENTER = enum.auto()
        RIGHT = enum.auto()


    _TEXT_ALIGN_CALLABLE = {
        Align.LEFT: lambda t, w: t,
        Align.CENTER: str.center,
        Align.RIGHT: str.rjust,
    }

    def __init__(self, text, text_align=Align.LEFT, paragraph_spacing=0,
                 truncate_with=' (...)', use_context=False, id=None,
                 template_slot=None, geometry=None, color=None, padding=None):

        super().__init__(id=id, template_slot=template_slot, geometry=geometry,
                         color=color, padding=padding)

        self._paragraphs = text if isinstance(text, (list, tuple)) else (text,)
        self._text_align_callable = self._TEXT_ALIGN_CALLABLE[text_align]
        self._paragraph_spacing = paragraph_spacing
        self._truncate_with = truncate_with
        self._use_context = use_context


        self._painted = False
        self._context = None


    def fill_window_contents(self, window):

        if self._painted:
            window.clear()

        y = self._pad_top
        available_width = window.width - self._pad_left - self._pad_right
        available_height = window.height - self._pad_top - self._pad_bottom

        wrap_callable = functools.partial(
            textwrap.wrap,
            width=available_width,
            placeholder=self._truncate_with,
        )

        # TODO: Stop processing if available_height gets to 0.
        for paragraph in self._paragraphs:
            if self._use_context:
                paragraph = paragraph.format(**self._context)
            for line in wrap_callable(paragraph, max_lines=available_height):
                line = self._text_align_callable(line, available_width)
                window.print(line, x=self._pad_left, y=y)
                y += 1
                available_height -= 1
            y += self._paragraph_spacing
            available_height -= 1

        self._painted = True


    async def handle_idle_next(self, template_slot_callable=None, render=True,
                               terminal_render=True, **context):

        await super().handle_idle_next(template_slot_callable=template_slot_callable, render=False)

        self._context = context
        self.fill_window_contents(self.window)
        self.window.add_resize_callback(self.fill_window_contents)

        await self.render(render=render, terminal_render=terminal_render)
        return 'done'


# ----------------------------------------------------------------------------
