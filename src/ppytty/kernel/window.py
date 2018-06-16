# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import functools

import pyte



class Window(object):

    def __init__(self, left, top, width, height, bg=None):

        self._left = left
        self._top = top
        self._width = width
        self._height = height
        self._bg = bg

        self._screen = pyte.Screen(width, height)
        self._stream = pyte.ByteStream(self._screen)


    def clear(self, how=2):

        self._screen.erase_in_display(how)
        self._screen.cursor_position()


    def write(self, text, x=None, y=None, fg=None, bg=None):

        attrs = []
        if fg:
            attrs.extend((38, 5, fg))
        if bg:
            attrs.extend((48, 5, bg))
        if attrs:
            self._screen.select_graphic_rendition(*attrs)

        if x is not None and y is not None:
            self._screen.cursor_position(y, x)

        self._screen.draw(text)

        if attrs:
            self._screen.select_graphic_rendition(0)


    def feed(self, data):

        self._stream.feed(data)


    def render(self, bt, full=False, encoding='utf8'):

        screen = self._screen
        screen_cursor = screen.cursor
        screen_buffer = screen.buffer
        left = self._left
        top = self._top
        width = self._width
        height = self._height
        window_bg = self._bg

        payload = [bt.hide_cursor]

        prev_char_format = ''
        line_numbers = range(height) if full else screen.dirty
        for line_no in line_numbers:
            line_data = screen_buffer[line_no]
            payload.append(bt.move(top+line_no, left))
            for column_no in range(width):
                char_data, fg, bg, bold, _, _, _, reverse = line_data[column_no]
                default_bg = window_bg
                if hasattr(window_bg, '__getitem__'):
                    default_bg = window_bg[line_no][column_no]
                char_format = self._char_format(bt, fg, bg, bold, reverse, default_bg)
                if char_format != prev_char_format:
                    payload.append(char_format)
                    prev_char_format = char_format
                payload.append(char_data)

        payload.append(bt.normal)
        payload.append(bt.move(top+screen_cursor.y, left+screen_cursor.x))
        if not screen_cursor.hidden:
            payload.append(bt.normal_cursor)
        screen.dirty.clear()
        return ''.join(payload).encode(encoding)


    # These will be used when rendering the pyte.Screen to a blessings generated
    # byte-string.

    _COLORS = {}
    for k, v in pyte.graphics.FG_ANSI.items():
        _COLORS[v] = k-30
    del _COLORS['default']
    for i, v in enumerate(pyte.graphics.FG_BG_256):
        _COLORS[v] = i


    @functools.lru_cache(maxsize=None)
    def _char_format(self, bt, fg, bg, bold, reverse, default_bg):

        colors = Window._COLORS
        parts = [bt.normal]
        if bold:
            parts.append(bt.bold)
        if reverse:
            parts.append(bt.reverse)
        fg_idx = colors.get(fg)
        if fg_idx is not None:
            parts.append(bt.color(fg_idx))
        bg_idx = colors.get(bg, default_bg)
        if bg_idx is not None:
            parts.append(bt.on_color(bg_idx))
        return ''.join(parts)
    

# ----------------------------------------------------------------------------