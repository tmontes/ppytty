
import sys
import textwrap

from ppytty.kernel import api



SLOW_PLAIN_OUTPUT = textwrap.dedent("""
    import time, sys

    for n in range(3):
        print('Hello', n)
        time.sleep(0.2)
    sys.exit(24)
""").strip()


FAST_COLORED_OUTPUT = textwrap.dedent("""
    import time, sys

    fg = '\033[38;5;'
    bg = '\033[48;5;'

    for i in range(256):
        n = str(i)
        fgstr = fg + n + 'm' + '%3s' % n
        bgstr = bg + n + 'm' 'XXXXXXXXXXXXXXXXXXX'
        print(fgstr, bgstr, '\033[0m')
    sys.exit(42)
""").strip()



async def ppytty_task():

    log_window = await api.window_create(0.1, 0.1, 0.8, 0.2, background=31)

    async def log(msg):
        log_window.print(msg + '\r\n')
        await api.window_render(log_window)

    process_window = await api.window_create(0.1, 0.3, 0.8, 0.6, background=0)
    await api.window_render(process_window)

    args = ['/usr/bin/vi']
    args = ['/usr/bin/top']
    args = [sys.executable, '-c', SLOW_PLAIN_OUTPUT]
    args = [sys.executable, '-c', FAST_COLORED_OUTPUT]

    p = await api.process_spawn(process_window, args)
    await log(f'Process spawned: {p!r}')

    sleep = 2
    await log(f'Sleeping for {sleep} seconds...')
    await api.sleep(sleep)

    await log(f'Waiting process termination...')
    c = await api.process_wait()
    await log(f'Waited: {c!r}, exit_code={c.exit_code}, signal={c.exit_signal}')

    await log('Any key to exit')
    await api.key_read()

