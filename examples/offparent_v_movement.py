
import random

from ppytty.kernel import api


async def window_moves():

    def w_top_bot_msg(w, msg):
        w.print(msg.center(w.width), x=0, y=0, bg=2)
        w.print(msg.center(w.width), x=0, y=w.height-1, bg=4)

    w = await api.window_create(0.3, 0, 0.4, 10, dy=-15, background=31)

    w_top_bot_msg(w, 'Started')
    await api.window_render(w)

    for s in range(w.parent.height + 30):
        w.move(dy=1)
        await api.window_render(w)
        w_top_bot_msg(w, f'Step {s}')
        await api.window_render(w)
        await api.sleep(0.05)


ppytty_task = window_moves
