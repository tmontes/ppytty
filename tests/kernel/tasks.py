# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api



async def sleep_zero():

    await api.sleep(0)



async def spawn_wait(task, sleep_before_wait=False):

    await api.task_spawn(task)
    if sleep_before_wait:
        await api.sleep(0)
    completed_task, success, result = await api.task_wait()
    return completed_task, success, result



async def sleep_zero_return_42_idiv_arg(arg):

    await api.sleep(0)
    return 42 // arg


# ----------------------------------------------------------------------------
