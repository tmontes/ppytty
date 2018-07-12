
import random

import ppytty


class WindowExerciser(ppytty.Task):

    async def run(self):

        w1 = await self.api.window_create(0.1, 0.1, 0.5, 0.5, background=31)
        w2 = await self.api.window_create(0.4, 0.4, 0.5, 0.5, background=39)

        w1.print('Bottom window'.center(w1.width), bg=17)
        w2.print('Top window'.center(w2.width), bg=19)

        w1.print(f'\x1b[2;{w1.height}r')  # TODO: implement as window.set_scroll_lines?
        w2.print(f'\x1b[2;{w2.height}r')
        w1.print('\x1b[2;1H')   # TODO: implement as window.move_cursor?
        w2.print('\x1b[2;1H')

        await self.api.window_render(w2)
        await self.api.sleep(0.5)
        await self.api.window_render(w1)
        await self.api.sleep(0.5)

        words = 'the quick brown fox jumps over the lazy dog'.split()
        windows = (w1, w2)
        for _ in range(w1.width*w1.height//2):
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



class Parent(ppytty.Task):

    async def run(self):

        child = WindowExerciser()
        await self.api.task_spawn(child)
        # await self.api.sleep(1)
        # await self.api.task_destroy(child)
        result = await self.api.task_wait()
        await self.api.direct_print(f'child result={result!r}')


ppytty_task = Parent()
