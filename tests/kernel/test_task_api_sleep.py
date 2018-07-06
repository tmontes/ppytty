# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import itertools as it

from ppytty.kernel import run, api

from . import helper_io



class TestSleep(helper_io.NoOutputAutoTimeTestCase):

    async def _sleeper(self, sleep_time):

        await api.sleep(sleep_time)


    def test_sleep(self):

        for sleep_time in (0, 0.5, 1, 10, -1):
            with self.subTest(sleep_time=sleep_time):
                task = self._sleeper(sleep_time)
                success, result = run(task)
                self.assertTrue(success)
                self.assertIsNone(result)


    async def _spawn_sleepers(self, sleeper1, sleeper2):

        await api.task_spawn(sleeper1)
        await api.task_spawn(sleeper2)
        completed_1st, _, _ = await api.task_wait()
        completed_2nd, _, _ = await api.task_wait()
        return completed_1st, completed_2nd


    def test_concurrent_sleeps(self):

        sleep_times = (-1, 0, 0.5, 1, 2, 3)
        for st1, st2 in it.product(sleep_times, sleep_times):
            with self.subTest(sleep_time1=st1, sleep_time2=st2):
                sleeper1 = self._sleeper(st1)
                sleeper2 = self._sleeper(st2)
                success, result = run(self._spawn_sleepers(sleeper1, sleeper2))
                self.assertTrue(success)
                completed_1st, completed_2nd = result
                # negative sleep times are equivalent to zero
                effective_st1 = max(st1, 0)
                effective_st2 = max(st2, 0)
                if effective_st1 < effective_st2:
                    self.assertEqual(completed_1st, sleeper1)
                    self.assertEqual(completed_2nd, sleeper2)
                elif effective_st1 > effective_st2:
                    self.assertEqual(completed_1st, sleeper2)
                    self.assertEqual(completed_2nd, sleeper1)
                else:
                    self.assertEqual(
                        {completed_1st, completed_2nd},
                        {sleeper1, sleeper2},
                    )


# ----------------------------------------------------------------------------
