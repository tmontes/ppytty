
import sys

from ppytty.kernel import api


async def window_resizes():

    w1 = await api.window_create(4, 2, 60, 15, bg=236)
    # p1 = await api.process_spawn(w1, ['/usr/bin/vi'])
    # p1 = await api.process_spawn(w1, ['/bin/bash'])
    p1 = await api.process_spawn(w1, [sys.executable])
    await api.window_render(w1)

    w2 = await api.window_create(50, 10, 30, 15, bg=39)
    for _ in range(42):
        w2.print('the quick brown fox jumps over the lazy dog ')
    w2.print('\r\n  KEY TO CONTINUE  \r\n\r\n', bg=173, fg=0)
    await api.window_render(w2)

    await api.key_read()

    import itertools as it

    try:
        for dw in it.cycle(it.chain(it.repeat(1, 7), it.repeat(-1, 7))):
            w1.resize(dw=dw)
            await api.window_render(w1, terminal_render=False)
            w2.resize(dw=dw)
            w2.move(dx=-dw)
            await api.window_render(w2)
            await api.sleep(0.1)
    except Exception as e:
        w2.print(f'ERROR: {e}')
        await api.window_render(w2)

    w2.print('\r\n  KEY TO EXIT  \r\n\r\n', bg=173, fg=0)
    await api.window_render(w2)
    await api.key_read()

    p1.terminate()
    await api.process_wait()
    await api.window_destroy(w1)



ppytty_task = window_resizes
