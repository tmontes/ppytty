
import random

from ppytty.kernel import api


async def window_moves():

    w = await api.window_create(0, 0.3, 20, 0.4, dx=-30, bg=31)

    words = 'the quick brown fox jumps over the lazy dog '
    for _ in range(4):
        w.print(words)
    await api.window_render(w)

    for _ in range(60 + w.parent.width):
        w.move(dx=1)
        await api.window_render(w)
        await api.sleep(0.01)


ppytty_task = window_moves
