# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import os
import sys

try:
    from pygments import highlight as pygm_highlight
    from pygments.lexers import get_lexer_by_name as pygm_get_lexer_by_name
    from pygments.styles import get_style_by_name as pygm_get_style_by_name
    from pygments.formatters import Terminal256Formatter as pygm_formatter
    from pygments.util import ClassNotFound as pygm_ClassNotFound
except ImportError:
    pygm_highlight = lambda code, lexer, formatter, outfile=None: code
    pygm_get_lexer_by_name = lambda _alias, **options: None
    pygm_get_style_by_name = lambda _name: None
    pygm_formatter = lambda **options: None
    pygm_ClassNotFound = ValueError
    pygments_imported = False
else:
    pygments_imported = True

from . import widget



class Code(widget.WindowWidget):

    def __init__(self, code=None, file_name=None, file_encoding='utf-8',
                 pygm_lexer_name='python3', pygm_style_name='paraiso-dark',
                 pygm_style=None, id=None, template_slot=None, geometry=None,
                 color=None, padding=None):

        super().__init__(id=id, template_slot=template_slot, geometry=geometry,
                         color=color, padding=padding)

        if code and file_name:
            raise ValueError(f'{self}: Pass in code or filename, not both.')

        self._code = code
        if file_name:
            caller_frame = sys._getframe(1)
            caller_file = caller_frame.f_globals.get('__file__')
            caller_file_dir = os.path.dirname(caller_file)
            file_name = os.path.join(caller_file_dir, file_name)
            with open(file_name, 'rt', encoding=file_encoding) as source:
                self._code = source.read()

        if not isinstance(self._code, str):
            raise ValueError(f'{self}: Code must be a string.')

        if not pygments_imported:
            self._log.warning('%r: Install pygments for syntax highlighting.', self)

        try:
            self._pygm_lexer = pygm_get_lexer_by_name(pygm_lexer_name)
        except pygm_ClassNotFound as e:
            msg = f'No pygments lexer named {pygm_lexer_name!r}'
            raise ValueError(msg) from e

        if pygm_style is None:
            try:
                pygm_style = pygm_get_style_by_name(pygm_style_name)
            except pygm_ClassNotFound as e:
                msg = f'No pygments style named {pygm_style_name!r}'
                raise ValueError(msg) from e

        self._pygm_formatter = pygm_formatter(style=pygm_style)

        self._painted = False


    def paint_window_contents(self, window):

        if self._painted:
            window.clear()

        y = self._pad_top
        available_width = window.width - self._pad_left - self._pad_right
        available_height = window.height - self._pad_top - self._pad_bottom

        highlighted_code = pygm_highlight(self._code, self._pygm_lexer, self._pygm_formatter)
        for highlighted_line in highlighted_code.splitlines():
            window.print(highlighted_line, x=self._pad_left, y=y)
            y += 1
            available_height -= 1

        self._painted = True


    async def handle_idle_next(self, template_slot_callable=None, render=True,
                               terminal_render=True, **context):

        await super().handle_idle_next(template_slot_callable=template_slot_callable, render=False)

        self.paint_window_contents(self.window)
        self.window.add_resize_callback(self.paint_window_contents)

        await self.render(render=render, terminal_render=terminal_render)
        return 'done'


# ----------------------------------------------------------------------------
