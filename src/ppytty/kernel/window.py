# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import copy
import functools

import pyte



class _SelfBlessingsTerminal(object):

    # This class is necessary due to a Python curses limitation: read on.
    #
    # Window objects have a render method that produces a byte-string
    # containing all the character data and formatting/cursor movement escape
    # codes representing the current Window contents. To do that, Window.render
    # needs to know the appropriate escape codes for the destination terminal.
    #
    # Blessings (https://github.com/erikrose/blessings) is a Python library
    # that helps with that: it produces the proper escape sequences for generic
    # terminal based output including formatting, cursor movement and more. It
    # uses curses' setupterm, tigetstr, tparm and friends to obtain the proper
    # escape codes for a given terminal, as long as it is present in the
    # system's terminfo database.
    #
    # With that, the generic actual output producing code would be:
    #
    # >>> w = Window(...)
    # >>> bt = blessings.Terminal(kind=os.environ['TERM'])
    # >>> data = w.render(bt)
    # >>> sys.stdout.write(data.encode(...))
    #
    # There is one more thing, though: Windows can be rendered onto other
    # Windows. Internally they wrap a pyte (https://github.com/selectel/pyte)
    # Screen and ByteStream which, collectivelly, implement a 'linux' terminal,
    # per the docs, but actually seems to support 'xterm-256color'. To render
    # a Window onto another Window the code would be:
    #
    # >>> parent = Window(...)
    # >>> child = Window(...)
    # >>> bt_child = blessings.Terminal(kind='linux')
    # >>> data = child.render(bt_child)
    # >>> parent.feed(data)
    #
    # And the Window to "real" terminal rendering, again:
    #
    # >>> bt_parent = blessings.Terminal(kind=os.environ['TERM'])
    # >>> data = parent.render(bt_parent)
    # >>> sys.stdout.write(data.encode(...))
    #
    # This would all be fine EXCEPT, like stated in the first comment line, it
    # does not work due to a Python curses limitation (which Blessings uses).
    # Here's a short demo, getting the "set forground color" escape sequence:
    #
    # >>> curses.setupterm('xterm-256color')
    # >>> curses.tparm(curses.tigetstr('setaf'), 31)
    # b'\x1b[38;5;31m'
    #
    # It first calls setupterm, then tigetstr/tparm to get that terminal's
    # escape sequences. The Python curses implementation has a LIMITATION in
    # that it discards subsequent calls to setupterm, preventing a program
    # from acessing the terminfo database for multiple terminal types.
    # (see https://bugs.python.org/issue7567#msg113216)

    # These were generated by hand with a Blessings Terminal instance with
    # kind='xterm-256color', which pyte's Screen/ByteStream handle nicely.

    hide_cursor = '\x1b[?25l'
    normal_cursor = '\x1b[?12l\x1b[?25h'

    normal = '\x1b(B\x1b[m'
    bold = '\x1b[1m'
    reverse = '\x1b[7m'

    @staticmethod
    def move(line, column):
        return f'\x1b[{line+1};{column+1}H'

    @staticmethod
    def color(fg_color):
        if fg_color < 8:
            return f'\x1b[{30+fg_color}m'
        elif fg_color < 16:
            return f'\x1b[{82+fg_color}m'
        elif fg_color < 256:
            return f'\x1b[38;5;{fg_color}m'
        else:
            raise ValueError(f'invalid fg_color: {fg_color}')

    @staticmethod
    def on_color(bg_color):
        if bg_color < 8:
            return f'\x1b[{40+bg_color}m'
        elif bg_color < 16:
            return f'\x1b[{92+bg_color}m'
        elif bg_color < 256:
            return f'\x1b[48;5;{bg_color}m'
        else:
            raise ValueError(f'invalid bg_color: {bg_color}')



class Window(object):

    def __init__(self, parent, x=0, y=0, w=1.0, h=1.0, dx=0, dy=0, dw=0, dh=0,
                 bg=None, no_cursor=True):

        # We don't really care about the parent itself; all we need is its `bt`
        # attribute so that we can:
        # - Get the parent's width/height.
        # - Produce the correct escape sequences when rendering.
        self._parent = parent

        # Used in focus highlights.
        self.title = None

        # Window geometry is defined by:
        # - Top left corner (x, y):
        #   - Positive ints map to 0-based absolute parent coords.
        #   - Positive floats map to 0-based relative parent coords.
        #     (where 1.0 is the first column/row after the visible ones)
        #   - Negative ints map to from-right/bottom absolute parent coords.
        #     (where -1 is the last column/row)
        #   - Negative floats map to from-right/bottom relative parent coords.
        #     (where -1.0 represents the first visible column/row)
        # - Width/Heigth (w/h):
        #   - Much like (x, y) where negative values are not expected to work!
        # - All values are updated by a delta: dx, dy, dw, dh.
        # See self._update_geometry()
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._dx = dx
        self._dy = dy
        self._dw = dw
        self._dh = dh
        self._update_geometry()

        # Track "uncovered" parent geometry after moves/resizes.
        self._update_last_render_geometry()

        # Called after we're resized and passed a single argument: self.
        self._resize_callbacks = []

        self._bg = bg

        self._screen = pyte.Screen(self._width, self._height)
        self._stream = pyte.ByteStream(self._screen)

        self._screen.cursor.hidden = no_cursor

        # Save the screen buffer to support highlight.
        self._save_buffer = None

        # My public `bt` so others can produce the correct escape sequences to
        # be processed by self.feed().
        self.bt = _SelfBlessingsTerminal


    def _update_geometry(self):

        def _rel_to_abs(value, limit, delta):
            if isinstance(value, float):
                value = int(value * limit)
            if value < 0:
                value = limit + value
            return value + delta

        parent_width = self._parent.width
        parent_height = self._parent.height

        self._left = _rel_to_abs(self._x, parent_width, self._dx)
        self._top =  _rel_to_abs(self._y, parent_height, self._dy)
        self._width = _rel_to_abs(self._w, parent_width, self._dw)
        self._height = _rel_to_abs(self._h, parent_height, self._dh)


    def _update_last_render_geometry(self):

        self._last_render_left = self._left
        self._last_render_top = self._top
        self._last_render_width = self._width
        self._last_render_height = self._height


    def __repr__(self):

        title = f'{repr(self.title)} ' if self.title else ''
        geometry = f'{self._width}x{self._height}'
        location = f'{self._left},{self._top}'
        return f'<Window {title}{geometry} @{location}>'


    @property
    def parent(self):

        return self._parent


    @property
    def left(self):

        return self._left


    @property
    def top(self):

        return self._top


    @property
    def width(self):

        return self._width


    @property
    def height(self):

        return self._height


    @property
    def cursor(self):

        return self._screen.cursor


    def overlaps(self, window):

        w_min_x = window._left
        w_max_x = w_min_x + window._width - 1
        w_min_y = window._top
        w_max_y = w_min_y + window._height - 1

        return self.overlaps_geometry(w_min_x, w_max_x, w_min_y, w_max_y)


    def overlaps_geometry(self, g_min_x, g_max_x, g_min_y, g_max_y):

        my_min_x = self._left
        my_max_x = my_min_x + self._width - 1
        my_min_y = self._top
        my_max_y = my_min_y + self._height - 1

        horizontal = (my_min_x <= g_max_x) and (my_max_x >= g_min_x)
        vertical = (my_min_y <= g_max_y) and (my_max_y >= g_min_y)

        return horizontal and vertical


    def uncovered_geometry(self):

        # Returns (min_x, min_y, max_x, max_y) tuple in parent coordinates if
        # the Window moved/resized such that it left "blanks" in the parent
        # since the last render; otherwise returns `None`.

        # IOW: if the current geometry fully "covers" the last rendered geometry
        # return `None`, otherwise return the last rendered geometry such that
        # callers know they might need to "erase/re-render" the uncovered area.

        cur_min_x = self._left
        cur_max_x = cur_min_x + self._width - 1
        cur_min_y = self._top
        cur_max_y = cur_min_y + self._height - 1
        lr_min_x = self._last_render_left
        lr_max_x = lr_min_x + self._last_render_width - 1
        lr_min_y = self._last_render_top
        lr_max_y = lr_min_y + self._last_render_height - 1

        horizontal_covered = (cur_min_x <= lr_min_x) and (cur_max_x >= lr_max_x)
        vertical_covered = (cur_min_y <= lr_min_y) and (cur_max_y >= lr_max_y)

        if horizontal_covered and vertical_covered:
            return None
        return lr_min_x, lr_max_x, lr_min_y, lr_max_y


    def clear(self, how=2):

        self._screen.erase_in_display(how)
        self._screen.cursor_position()


    def erase_geometry(self, min_x, max_x, min_y, max_y):

        self_screen = self._screen
        self_screen_buffer = self_screen.buffer
        self_screen_dirty = self_screen.dirty

        from_x = max(0, min_x)
        to_x = min(self._width, max_x+1)

        from_y = max(0, min_y)
        to_y = min(self._height, max_y+1)

        for y in range(from_y, to_y):
            for x in range(from_x, to_x):
                del self_screen_buffer[y][x]
            self_screen_dirty.add(y)


    def highlight(self, clear=False):

        if not clear:
            self._save_buffer = copy.deepcopy(self._screen.buffer)
            self._screen.save_cursor()
            self._screen.cursor.hidden = True
            text = str(self.title or self)
            self.print(text, x=0, y=self._height-1, fg=0, bg=255)
        else:
            self._screen.select_graphic_rendition()
            self._screen.restore_cursor()
            self._screen.buffer = self._save_buffer
            self._save_buffer = None


    def print(self, text, x=None, y=None, fg=None, bg=None):

        attrs = []
        if fg is not None:
            attrs.extend((38, 5, fg))
        if bg is not None:
            attrs.extend((48, 5, bg))
        if attrs:
            self._screen.select_graphic_rendition(*attrs)

        if x is not None and y is not None:
            self._screen.cursor_position(y+1, x+1)

        self._stream.feed(text.encode('utf8'))

        if attrs:
            self._screen.select_graphic_rendition(0)


    def move(self, x=None, y=None, dx=0, dy=0):

        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        self._dx += dx
        self._dy += dy
        self._update_geometry()


    def resize(self, w=None, h=None, dw=0, dh=0):

        if w is not None:
            self._w = w
        if h is not None:
            self._h = h
        self._dw += dw
        self._dh += dh
        self._update_geometry()
        self._screen.resize(self._height, self._width)
        for callback in self._resize_callbacks:
            # TODO: Handle exceptions? Remove failing? Log and ignore/re-raise?
            callback(self)


    def add_resize_callback(self, callback):

        self._resize_callbacks.append(callback)


    def feed(self, data):

        self._stream.feed(data)


    def render(self, full=False, encoding='utf8', cursor_only=False, do_cursor=False):

        # full: if True, renders all lines; otherwise, renders changed lines.
        # cursor_only: if True, renders no lines, but renders the cursor.
        # do_cursor: if True, cursor is rendered with or without rendered lines.

        self_parent = self._parent
        screen = self._screen
        screen_cursor = screen.cursor
        screen_buffer = screen.buffer
        screen_dirty = screen.dirty
        left = self._left
        render_left = max(0, left)
        top = self._top
        window_bg = self._bg

        bt = self_parent.bt
        bt_move = bt.move
        self_char_format = self._char_format

        payload = []
        payload_append = payload.append

        if cursor_only:
            line_numbers = ()
        else:
            # Do not render lines outside of parent geometry
            if full:
                min_line = max(0, -top)
                max_line = min(self._height, self_parent.height - top)
                line_numbers = range(min_line, max_line)
            else:
                line_numbers = {
                    line_no for line_no in screen_dirty
                    if -top <= line_no < self_parent.height - top
                }

        if line_numbers or cursor_only or do_cursor:
            payload_append(bt.hide_cursor)

        # Do not render columns outside of parent geometry
        min_column = max(0, -left)
        max_column = min(self._width, self_parent.width - left)
        column_numbers = range(min_column, max_column)

        prev_char_format = ''
        for line_no in line_numbers:
            line_data = screen_buffer[line_no]
            payload_append(bt_move(top+line_no, render_left))
            for column_no in column_numbers:
                char_data, fg, bg, bold, _, _, _, reverse = line_data[column_no]
                default_bg = window_bg
                if hasattr(window_bg, '__getitem__'):
                    default_bg = window_bg[line_no][column_no]
                char_format = self_char_format(bt, fg, bg, bold, reverse, default_bg)
                if char_format != prev_char_format:
                    payload_append(char_format)
                    prev_char_format = char_format
                payload_append(char_data)

        if line_numbers or cursor_only or do_cursor:
            payload_append(bt.normal)
            # TODO: Improve cursor handling if outside parent geometry.
            payload_append(bt_move(max(0, top+screen_cursor.y), render_left+screen_cursor.x))
            if not screen_cursor.hidden:
                payload_append(bt.normal_cursor)

        screen_dirty.clear()
        self._update_last_render_geometry()

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

        colors = self._COLORS
        parts = [bt.normal]
        parts_append = parts.append
        if bold:
            parts_append(bt.bold)
        if reverse:
            parts_append(bt.reverse)
        fg_idx = colors.get(fg)
        if fg_idx is not None:
            parts_append(bt.color(fg_idx))
        bg_idx = colors.get(bg, default_bg)
        if bg_idx is not None:
            parts_append(bt.on_color(bg_idx))
        return ''.join(parts)


# ----------------------------------------------------------------------------
