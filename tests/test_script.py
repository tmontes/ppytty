# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

import ppytty



class TestFlatScript(unittest.TestCase):

    def setUp(self):
        self.script = ppytty.Script([
            '1',
            '2',
            '3',
        ])

    def test_start(self):
        result = self.script.start()
        self.assertEqual(result, '1')

    def test_next(self):
        result = self.script.next_step()
        self.assertEqual(result, '2')

    def test_next_next(self):
        _ = self.script.next_step()
        result = self.script.next_step()
        self.assertEqual(result, '3')

    def test_next_next_next(self):
        _ = self.script.next_step()
        _ = self.script.next_step()
        with self.assertRaises(ValueError):
            _ = self.script.next_step()

    def test_next_prev(self):
        _ = self.script.next_step()
        result = self.script.prev_step()
        self.assertEqual(result, '1')

    def test_prev(self):
        with self.assertRaises(ValueError):
            _ = self.script.prev_step()

    def test_last(self):
        result = self.script.last_step()
        self.assertEqual(result, '3')

    def test_next_next_first(self):
        _ = self.script.next_step()
        _ = self.script.next_step()
        result = self.script.first_step()
        self.assertEqual(result, '1')


# ----------------------------------------------------------------------------
