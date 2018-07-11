
import random

import ppytty


class WindowExerciser(ppytty.Task):

    async def run(self):

        w1 = await self.api.window_create(5, 3, 40, 15, 31)
        w2 = await self.api.window_create(35, 12, 40, 15, 39)

        w1.print('Bottom window'.center(40), bg=17)
        w2.print('Top window'.center(40), bg=19)

        w1.print('\x1b[2;15r')  # TODO: implement as window.set_scroll_lines?
        w2.print('\x1b[2;15r')
        w1.print('\x1b[2;1H')   # TODO: implement as window.move_cursor?
        w2.print('\x1b[2;1H')

        await self.api.window_render(w2)
        await self.api.sleep(0.2)
        await self.api.window_render(w1)

        await self.api.sleep(0.2)

        words = 'the quick brown fox jumps over the lazy dog'.split()
        windows = (w1, w2)

        for _ in range(42):
            window = random.choice(windows)
            word = random.choice(words)
            window.print(word + ' ')
            await self.api.window_render(window)
            await self.api.sleep(0.05)

        await self.api.window_destroy(w1)

        await self.api.state_dump('MY TAG')

        await self.api.sleep(2)


class Parent(ppytty.Task):

    async def run(self):

        child = WindowExerciser()
        await self.api.task_spawn(child)
        # await self.api.sleep(1)
        # await self.api.task_destroy(child)
        result = await self.api.task_wait()
        await self.api.direct_print(f'child result={result!r}')


ppytty_task = Parent()
