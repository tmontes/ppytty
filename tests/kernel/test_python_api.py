# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import run



def _sleep_zero_task():

    yield ('sleep', 0)



def _spawn_sleep_zero_task_via_function():

    generator_function = _sleep_zero_task
    yield ('task-spawn', generator_function)
    yield ('task-wait',)



def _spawn_sleep_zero_task_via_object():

    generator_object = _sleep_zero_task()
    yield ('task-spawn', generator_object)
    yield ('task-wait',)



class TestRun(unittest.TestCase):

    def test_gen_function(self):

        generator_function = _sleep_zero_task
        run(generator_function, post_prompt='')


    def test_gen_object(self):

        generator_object = _sleep_zero_task()
        run(generator_object, post_prompt='')


    def test_gen_function_spawn_gen_function(self):

        generator_function = _spawn_sleep_zero_task_via_function
        run(generator_function, post_prompt='')


    def test_gen_function_spawn_gen_object(self):

        generator_function = _spawn_sleep_zero_task_via_object
        run(generator_function, post_prompt='')


    def test_gen_object_spawn_gen_function(self):

        generator_function = _spawn_sleep_zero_task_via_function()
        run(generator_function, post_prompt='')


    def test_gen_object_spawn_gen_object(self):

        generator_function = _spawn_sleep_zero_task_via_object()
        run(generator_function, post_prompt='')


# ----------------------------------------------------------------------------
