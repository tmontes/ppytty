
import random

from ppytty.kernel import api


async def window_moves():

    w1 = await api.window_create(17, 3, 30, 15, background=31)
    w2 = await api.window_create(40, 10, 30, 15, background=39)

    words = 'the quick brown fox jumps over the lazy dog'.split()
    windows = (w1, w2)
    for _ in range(42):
        window = random.choice(windows)
        word = random.choice(words)
        window.print(word + ' ')
    w2.print('\r\n\r\n  KEY TO START MOVING  ', bg=173, fg=0)
    await api.window_render(w1)
    await api.window_render(w2)
    await api.key_read()

    for _ in range(15):
        w2.move(dx=-2, dy=-1 if random.random()<0.4 else 0)
        await api.window_render(w2, terminal_render=False)
        w1.move(dx=2, dy=1 if random.random()<0.5 else 0)
        await api.window_render(w1)
        await api.sleep(0.02)


    w1.print('\r\n\r\n  KEY TO GET OUT  ', bg=17)
    await api.window_render(w1)
    await api.key_read()


ppytty_task = window_moves
