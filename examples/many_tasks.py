
import itertools

from ppytty.kernel import api



async def runner(name, left):

    n = 0
    w = await api.window_create(left, 3, 20, 4, bg=31)
    w.print(name.center(20), bg=0)
    while True:
        w.print(str(n).center(20), 0, 2)
        await api.window_render(w)
        n += 1


async def sleeper():

    w = await api.window_create(5, 10, 20, 4, bg=31)
    bg = 0
    while True:
        w.print('Sleeper'.center(20), x=0, y=0, bg=bg)
        await api.window_render(w)
        await api.sleep(1)
        bg = 6-bg


async def reader():

    w = await api.window_create(30, 10, 20, 4, bg=31)
    w.print('Reader'.center(20), bg=0)
    await api.window_render(w)
    while True:
        kb = await api.key_read()
        w.print(f'read {kb!r}'.center(20), x=0, y=2)
        await api.window_render(w)


async def receiver():

    w = await api.window_create(55, 10, 20, 4, bg=31)
    w.print('Receiver'.center(20), bg=0)
    await api.window_render(w)
    while True:
        _, msg = await api.message_wait()
        w.print(f'got {msg!r}'.center(20), x=0, y=2)
        await api.window_render(w)


async def ppytty_task():

    await api.task_spawn(runner('Runner 1', 5))
    await api.task_spawn(runner('Runner 2', 30))
    await api.task_spawn(runner('Runner 3', 55))
    await api.task_spawn(sleeper)
    await api.task_spawn(reader)
    await api.task_spawn(receiver)

    for n in itertools.cycle(range(5)):
        await api.sleep(1.3)
        await api.message_send(receiver, f'hello {n}')


