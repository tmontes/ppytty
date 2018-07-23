
import random

import ppytty


class WindowExerciser(ppytty.Task):

    def w1_repaint(self, w):
        # can only call methods on w
        w.print('Bottom window'.center(w.width), x=0, y=0, bg=17)

    def w2_repaint(self, w):
        # can only call methods on w
        w.print('Top window'.center(w.width), x=0, y=0, bg=19)

    async def run(self):
        w1 = await self.api.window_create(0.1, 0.1, 0.4, 0.4, background=31)
        w2 = await self.api.window_create(0.4, 0.4, 0.4, 0.4, background=39)

        w1.add_resize_callback(self.w1_repaint)
        w2.add_resize_callback(self.w2_repaint)

        self.w1_repaint(w1)
        self.w2_repaint(w2)

        w1.print(f'\x1b[2;{w1.height}r')  # TODO: implement as window.set_scroll_lines?
        w2.print(f'\x1b[2;{w2.height}r')
        w1.print('\x1b[2;1H')   # TODO: implement as window.move_cursor?
        w2.print('\x1b[2;1H')

        await self.api.window_render(w2)
        await self.api.sleep(0.5)
        await self.api.window_render(w1)

        words = 'the quick brown fox jumps over the lazy dog'.split()
        windows = (w1, w2)
        for _ in range(int(w1.width*w1.height//5.5)):
            window = random.choice(windows)
            word = random.choice(words)
            window.print(word + ' ')
            await self.api.window_render(window)
            await self.api.sleep(0.01)

        w1.print(f'\r\n\r\n  ME: {w1.width}x{w1.height}  ', bg=130, fg=8)
        await self.api.window_render(w1)

        w2.print(f'\r\n\r\n ME: {w2.width}x{w2.height} \r\n', bg=0, fg=13)
        w2.print(f' PARENT: {w2.parent.width}x{w2.parent.height}  ', bg=0, fg=15)
        w2.print('  [ANY KEY TO END]')
        await self.api.window_render(w2)

        await self.api.key_read()

        await self.api.window_destroy(w1)
        await self.api.key_read()



class Parent(ppytty.Task):

    async def run(self):

        child = WindowExerciser()
        await self.api.task_spawn(child)
        # await self.api.sleep(1)
        # await self.api.task_destroy(child)
        result = await self.api.task_wait()
        await self.api.direct_print(f'child result={result!r}')


ppytty_task = Parent()
