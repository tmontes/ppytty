# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import sys

from ppytty.kernel import run, api

from . import helper_io



class Tests(helper_io.NoOutputTestCase):

    @staticmethod
    def _sleeper_process_args(seconds):

        python_source_code = f"""
            import time
            time.sleep({seconds})
        """
        return [sys.executable, '-c', python_source_code]


    def test_spawn_wait(self):

        async def task():

            window = await api.window_create(0, 0, 80, 25)
            args = self._sleeper_process_args(0)
            process = await api.process_spawn(window, args)
            completed_process = await api.process_wait()
            await api.window_destroy(window)
            return process, completed_process

        success, result = run(task)

        self.assertTrue(success)
        spawned_process, completed_process = result
        self.assertIs(spawned_process, completed_process)


    def test_spawn_signal_wait(self):

        raise NotImplementedError()



class TestOddCases(helper_io.NoOutputTestCase):

    def test_spawn_process_and_terminate_task(self):

        raise NotImplementedError()


    def test_child_task_spawns_and_is_destroyed(self):

        raise NotImplementedError()


# ----------------------------------------------------------------------------
