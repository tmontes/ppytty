# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------



def sleep_zero():

    yield ('sleep', 0)



def spawn_wait(task, sleep_before_wait=False):

    yield ('task-spawn', task)
    if sleep_before_wait:
        yield ('sleep', 0)
    completed_task, success, result = yield ('task-wait',)
    return completed_task, success, result



def sleep_zero_return_42_idiv_arg(arg):

    yield ('sleep', 0)
    return 42 // arg


# ----------------------------------------------------------------------------
