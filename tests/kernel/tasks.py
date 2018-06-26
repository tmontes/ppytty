# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------



def sleep_zero():

    yield ('sleep', 0)



def spawn_sleep_zero_gen_function():

    generator_function = sleep_zero
    yield ('task-spawn', generator_function)
    yield ('task-wait',)



def spawn_sleep_zero_gen_object():

    generator_object = sleep_zero()
    yield ('task-spawn', generator_object)
    yield ('task-wait',)



def sleep_zero_return_42_idiv_arg(arg):

    yield ('sleep', 0)
    return 42 // arg


# ----------------------------------------------------------------------------
