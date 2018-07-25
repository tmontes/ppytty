
import random

from ppytty.kernel import api
from ppytty.lib import Task


async def window_exerciser():

    def w1_repaint(w):
        # can only call methods on w
        w.print('Bottom window'.center(w.width), x=0, y=0, bg=17)

    def w2_repaint(w):
        # can only call methods on w
        w.print('Top window'.center(w.width), x=0, y=0, bg=19)

    w1 = await api.window_create(0.1, 0.1, 0.5, 0.5, bg=31)
    w2 = await api.window_create(0.4, 0.4, 0.5, 0.5, bg=39)

    w1.add_resize_callback(w1_repaint)
    w2.add_resize_callback(w2_repaint)

    w1_repaint(w1)
    w2_repaint(w2)

    w1.print(f'\x1b[2;{w1.height}r')  # TODO: implement as window.set_scroll_lines?
    w2.print(f'\x1b[2;{w2.height}r')
    w1.print('\x1b[2;1H')   # TODO: implement as window.move_cursor?
    w2.print('\x1b[2;1H')

    await api.window_render(w2)
    await api.sleep(0.5)
    await api.window_render(w1)

    words = 'the quick brown fox jumps over the lazy dog'.split()
    windows = (w1, w2)
    for _ in range(int(w1.width*w1.height//5.5)):
        window = random.choice(windows)
        word = random.choice(words)
        window.print(word + ' ')
        await api.window_render(window)
        await api.sleep(0.01)

    w1.print(f'\r\n\r\n  ME: {w1.width}x{w1.height}  ', bg=130, fg=8)
    await api.window_render(w1)

    w2.print(f'\r\n\r\n ME: {w2.width}x{w2.height} \r\n', bg=0, fg=13)
    w2.print(f' PARENT: {w2.parent.width}x{w2.parent.height}  ', bg=0, fg=15)
    w2.print('  [ANY KEY TO END]')
    await api.window_render(w2)

    await api.key_read()

    await api.window_destroy(w1)
    await api.key_read()



async def parent():

    await api.task_spawn(window_exerciser)
    # await api.sleep(1)
    # await api.task_destroy(child)
    result = await api.task_wait()
    await api.direct_print(f'child result={result!r}')


ppytty_task = parent
