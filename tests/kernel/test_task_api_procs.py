# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import textwrap
import signal
import sys

from ppytty.kernel import run, api

from . import helper_io



class Tests(helper_io.NoOutputTestCase):

    @staticmethod
    def _sleeper_process_args(seconds):

        python_source_code = textwrap.dedent(f"""
            import time, sys
            time.sleep({seconds})
            sys.exit(42)
        """).strip()
        return [sys.executable, '-c', python_source_code]


    async def _spawn_sleep_wait(self, sleep_before_wait, process_sleep):

        window = await api.window_create(0, 0, 80, 25)
        args = self._sleeper_process_args(process_sleep)
        spawned_process = await api.process_spawn(window, args)
        await api.sleep(sleep_before_wait)
        completed_process = await api.process_wait()
        await api.window_destroy(window)
        return spawned_process, completed_process


    def test_spawn_wait_process_ends(self):

        success, result = run(self._spawn_sleep_wait(0, 0.1))

        self.assertTrue(success)
        spawned_process, completed_process = result
        self.assertIs(spawned_process, completed_process)
        self.assertEqual(completed_process.exit_code, 42)
        self.assertEqual(completed_process.exit_signal, 0)


    def test_spawn_process_ends_wait(self):

        # Test is somewhat fragile
        # Ideally it should exercise the "process terminates before our task
        # waits for it" code path. It might not, if the spawning is too slow.

        success, result = run(self._spawn_sleep_wait(0.1, 0))

        self.assertTrue(success)
        spawned_process, completed_process = result
        self.assertIs(spawned_process, completed_process)
        self.assertEqual(completed_process.exit_code, 42)
        self.assertEqual(completed_process.exit_signal, 0)


    async def _signal_test_task(self, send_signal_callable):

        window = await api.window_create(0, 0, 80, 25)
        args = self._sleeper_process_args(42)
        spawned_process = await api.process_spawn(window, args)
        # TODO: Something not 100% clear going on here.
        # Tests running this task fail "randomly". This sleep seems to help.
        await api.sleep(0.001)
        send_signal_callable(spawned_process)
        completed_process = await api.process_wait()
        await api.window_destroy(window)
        return completed_process


    def test_spawn_terminate_wait(self):

        task = self._signal_test_task(lambda p: p.terminate())
        success, completed_process = run(task)

        self.assertTrue(success, f'non-success result: {completed_process!r}')
        self.assertEqual(completed_process.exit_signal, signal.SIGTERM)
        self.assertEqual(completed_process.exit_code, 0)


    def test_spawn_kill_wait(self):

        task = self._signal_test_task(lambda p: p.kill())
        success, completed_process = run(task)

        self.assertTrue(success, f'non-success result: {completed_process!r}')
        self.assertEqual(completed_process.exit_signal, signal.SIGKILL)
        self.assertEqual(completed_process.exit_code, 0)


    def test_spawn_sigusr1_wait(self):

        task = self._signal_test_task(lambda p: p.signal(signal.SIGUSR1))
        success, completed_process = run(task)

        self.assertTrue(success, f'non-success result: {completed_process!r}')
        self.assertEqual(completed_process.exit_signal, signal.SIGUSR1)
        self.assertEqual(completed_process.exit_code, 0)



class TestOddCases(helper_io.NoOutputTestCase):

    def test_spawn_process_and_terminate_task(self):

        raise NotImplementedError()


    def test_child_task_spawns_and_is_destroyed(self):

        raise NotImplementedError()


# ----------------------------------------------------------------------------
