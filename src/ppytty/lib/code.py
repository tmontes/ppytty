# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


import os
import sys

from . import widget



class Code(widget.WindowWidget):

    def __init__(self, code=None, file_name=None, file_encoding='utf-8', id=None,
                 template_slot=None, geometry=None, color=None, padding=None):

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

        self._painted = False


    def paint_window_contents(self, window):

        if self._painted:
            window.clear()

        # TODO: actually paint

        # Brought in from the Text widget, will certainly be of use:

        # y = self._pad_top
        # available_width = window.width - self._pad_left - self._pad_right
        # available_height = window.height - self._pad_top - self._pad_bottom

        # For now just print something.

        window.print(self._code.replace('\n', '\r\n'))

        self._painted = True


    async def handle_idle_next(self, template_slot_callable=None, render=True,
                               terminal_render=True, **context):

        await super().handle_idle_next(template_slot_callable=template_slot_callable, render=False)

        self.paint_window_contents(self.window)
        self.window.add_resize_callback(self.paint_window_contents)

        await self.render(render=render, terminal_render=terminal_render)
        return 'done'


# ----------------------------------------------------------------------------
