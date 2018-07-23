
import sys

from ppytty.kernel import api



async def ppytty_task():

    log_win = await api.window_create(0, 0, 1.0, 8, dx=2, dy=1, dw=-4, background=31)

    async def log(msg):
        log_win.print(msg + '\r\n')
        await api.window_render(log_win)

    p1_win = await api.window_create(0, 10, 0.5, 1.0, dx=2, dw=-3, dh=-11, background=0)
    p1_win.title = '/bin/bash'
    p1 = await api.process_spawn(p1_win, ['/bin/bash'])
    await log(f'Process spawned: {p1!r}')

    p2_win = await api.window_create(0.5, 10, 0.5, 1.0, dx=1, dw=-3, dh=-11, background=4)
    p2_win.title = 'Python REPL'
    p2 = await api.process_spawn(p2_win, [sys.executable])
    await log(f'Process spawned: {p2!r}')

    async def stop_process(p, p_w):
        await log(f'Terminating: {p!r}')
        p.terminate()
        c = await api.process_wait()
        await log(f'Waited: {c!r}, exit_code={c.exit_code}, signal={c.exit_signal}')
        await api.sleep(0.1)
        await api.window_destroy(p_w)
        

    await log('Type "L" or "R" to stop left/right process.')
    while True:
        key = await api.key_read()
        if key == b'L' and p1.exit_code is None:
            await stop_process(p1, p1_win)
        elif key == b'R' and p2._exit_code is None:
            await stop_process(p2, p2_win)
        elif key == b'.':
            break
