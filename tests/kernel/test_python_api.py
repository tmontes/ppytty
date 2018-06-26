# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import unittest

from ppytty import run

from . import tasks



class TestRun(unittest.TestCase):

    def test_gen_function(self):

        generator_function = tasks.sleep_zero
        run(generator_function)


    def test_gen_object(self):

        generator_object = tasks.sleep_zero()
        run(generator_object)


    def test_gen_function_spawn_gen_function(self):

        generator_function = tasks.spawn_sleep_zero_gen_function
        run(generator_function)


    def test_gen_function_spawn_gen_object(self):

        generator_function = tasks.spawn_sleep_zero_gen_object
        run(generator_function)


    def test_gen_object_spawn_gen_function(self):

        generator_object = tasks.spawn_sleep_zero_gen_function()
        run(generator_object)


    def test_gen_object_spawn_gen_object(self):

        generator_object = tasks.spawn_sleep_zero_gen_object()
        run(generator_object)


# ----------------------------------------------------------------------------
