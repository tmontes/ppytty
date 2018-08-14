# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import functools
import os
import sys

try:
    from pygments import highlight as pygm_highlight
    from pygments.lexers import get_lexer_by_name as pygm_get_lexer_by_name
    from pygments.styles import get_style_by_name as pygm_get_style_by_name
    from pygments.formatters import Terminal256Formatter as pygm_Formatter
    from pygments.util import ClassNotFound as pygm_ClassNotFound
except ImportError:
    pygm_highlight = lambda code, lexer, formatter, outfile=None: code.strip()
    pygm_get_lexer_by_name = lambda _alias, **options: None
    pygm_get_style_by_name = lambda _name: None
    pygm_Formatter = lambda **options: None
    pygm_ClassNotFound = ValueError
    pygments_imported = False
else:
    pygments_imported = True

from . import widget



class Code(widget.WindowWidget):

    def __init__(self, code=None, file_name=None, file_encoding='utf-8',
                 wrap=True, truncate_line_with='\N{HORIZONTAL ELLIPSIS}',
                 truncate_code_with='... ', line_numbers=False, line_number_fmt='2d',
                 line_number_prefix=' ', line_number_suffix=' ', line_number_fg=None,
                 line_number_bg=None, first_line=1,
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

        self._wrap = wrap
        self._truncate_line_with = truncate_line_with
        self._truncate_line_len = len(truncate_line_with)
        self._truncate_code_with = truncate_code_with
        self._truncate_code_len = len(truncate_code_with)

        self._line_numbers = line_numbers
        self._line_number_fmt = line_number_fmt
        self._line_number_prefix = line_number_prefix
        self._line_number_suffix = line_number_suffix
        self._line_number_fg = line_number_fg
        self._line_number_bg = line_number_bg

        self._first_line = first_line

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

        self._pygm_formatter = pygm_Formatter(style=pygm_style)

        self._painted = False


    @functools.lru_cache(maxsize=None)
    def _line_number_str(self, n):

        return f'{self._line_number_prefix}{n:{self._line_number_fmt}}{self._line_number_suffix}'


    def paint_window_contents(self, window):

        if self._painted:
            window.clear()

        y = self._pad_top

        pad_left = self._pad_left
        pad_right = self._pad_right
        pad_bottom = self._pad_bottom

        available_height = window.height - y - pad_bottom
        available_width = window.width - pad_left - pad_right

        # Speed up repeated attribute access
        max_x = window.width - pad_right
        window_cursor = window.cursor
        window_print = window.print
        self_wrap = self._wrap
        if not self_wrap:
            truncate_line_with =  self._truncate_line_with
            truncate_x = max_x - self._truncate_line_len

        # Output strategy:
        # - Split highlighted code into lines (ANSI escapes don't change that).
        # - Divide each line into fits_for_sure + remaining, at available_width.
        #   - Most probably even though fits_for_sure has up to available_width
        #     characters, it will not fill the available horizontal space due to
        #     the fact that it includes ANSI escape sequences.
        #   - From there, we output one character at a time from remaining,
        #     wrapping into a new line or truncating once the window cursor
        #     reaches the maximum x defined by window geometry and padding.
        # - Along the way, track in which window line each line_number is
        #   displayed in the y_and_line_numbers list, to do a final pass in
        #   printing the line numbers, if activated (important: line numbers
        #   can only be printed last, otherwise they would either affect or be
        #   affected by the code color formatting).

        fit_available_height = True

        hl_code = pygm_highlight(self._code, self._pygm_lexer, self._pygm_formatter)
        hl_lines = hl_code.splitlines()

        line_number = self._first_line
        if line_number > 1:
            hl_lines = hl_lines[line_number-2:]
        y_and_line_numbers = []

        if self._line_numbers:
            # Determine how much width displaying line numbers will consume.
            max_line_number = line_number + len(hl_lines) - 1
            line_number_width = len(self._line_number_str(max_line_number))
            available_width -= line_number_width
            pad_left += line_number_width

        for hl_line in hl_lines:
            if not available_height:
                fit_available_height = False
                break
            fits_for_sure, remaining = hl_line[:available_width], hl_line[available_width:]
            y_and_line_numbers.append((y, line_number))
            window_print(fits_for_sure, x=pad_left, y=y)
            for each in remaining:
                if window_cursor.x < max_x:
                    window_print(each)
                elif self_wrap:
                    y += 1
                    available_height -= 1
                    if not available_height:
                        fit_available_height = False
                        break
                    y_and_line_numbers.append((y, None))
                    window_print(each, x=pad_left, y=y)
                else:
                    window_print(truncate_line_with, x=truncate_x, y=y)
            if not fit_available_height:
                break
            y += 1
            available_height -= 1
            line_number += 1

        if not fit_available_height:
            truncate_code_with = self._truncate_code_with
            truncate_code_len = self._truncate_code_len
            line = truncate_code_with * (available_width // truncate_code_len + 1)
            # If the output is truncated not only will we display the
            # truncate_code_with string, but also -- importantly -- we reset
            # the output formatting first; otherwise, any pending colorization
            # might be extended to the truncation string and subsequent output
            line = window.bt.normal + line[:available_width]
            window_print(line, x=pad_left, y=window.height-pad_bottom-1)

        if self._line_numbers:
            # Let's print the line numbers now.
            fg = self._line_number_fg
            bg = self._line_number_bg
            blank_count = line_number_width - len(self._line_number_suffix)
            wrap_str = ' ' * blank_count + self._line_number_suffix
            pad_left -= line_number_width
            for y, line_number in y_and_line_numbers:
                line = self._line_number_str(line_number) if line_number else wrap_str
                window_print(line, x=pad_left, y=y, fg=fg, bg=bg)

        self._painted = True


    async def handle_idle_next(self, template_slot_callable=None, render=True,
                               terminal_render=True, **context):

        await super().handle_idle_next(template_slot_callable=template_slot_callable, render=False)

        self.paint_window_contents(self.window)
        self.window.add_resize_callback(self.paint_window_contents)

        await self.render(render=render, terminal_render=terminal_render)
        return 'done'


# ----------------------------------------------------------------------------
