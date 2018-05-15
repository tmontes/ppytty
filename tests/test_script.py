# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

import ppytty



class TestScript(unittest.TestCase):

    def test_default_repr(self):
        script = ppytty.Script([])
        result = repr(script)
        name = hex(id(script))
        self. assertEqual(result, f'<Script {name}>')

    def test_named_repr(self):
        script = ppytty.Script([], name='script-name')
        result = repr(script)
        self.assertEqual(result, "<Script 'script-name'>")



class TestFlatScript(unittest.TestCase):

    def setUp(self):
        self.script = ppytty.Script([
            '1',
            '2',
            '3',
        ])

    def test_first(self):
        result = self.script.first_step()
        self.assertEqual(result, '1')

    def test_current(self):
        result = self.script.current_step()
        self.assertEqual(result, '1')

    def test_first_current(self):
        _ = self.script.first_step()
        result = self.script.current_step()
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
        with self.assertRaises(ppytty.ScriptLimit):
            _ = self.script.next_step()

    def test_next_prev(self):
        _ = self.script.next_step()
        result = self.script.prev_step()
        self.assertEqual(result, '1')

    def test_prev(self):
        with self.assertRaises(ppytty.ScriptLimit):
            _ = self.script.prev_step()

    def test_last(self):
        result = self.script.last_step()
        self.assertEqual(result, '3')

    def test_next_next_first(self):
        _ = self.script.next_step()
        _ = self.script.next_step()
        result = self.script.first_step()
        self.assertEqual(result, '1')



class TestNestedScript(unittest.TestCase):

    def setUp(self):
        self.script = ppytty.Script([
            ppytty.Script(['1-1', '1-2']),
            ppytty.Script(['2-1', '2-2', '2-3']),
            ppytty.Script(['3-1', '3-2']),
        ])
        self.linear = [
            '1-1', '1-2',
            '2-1', '2-2', '2-3',
            '3-1', '3-2',
        ]

    def test_first(self):
        result = self.script.first_step()
        self.assertEqual(result, '1-1')

    def test_first_current(self):
        _ = self.script.first_step()
        result = self.script.current_step()
        self.assertEqual(result, '1-1')

    def test_first_and_all_nexts(self):
        result = self.script.first_step()
        self.assertEqual(result, self.linear[0])
        for times, expected in enumerate(self.linear[1:], start=1):
            with self.subTest(times=times, expected=expected):
                result = self.script.next_step()
                self.assertEqual(result, expected)
        with self.assertRaises(ppytty.ScriptLimit):
            _ = self.script.next_step()

    def test_last(self):
        result = self.script.last_step()
        self.assertEqual(result, '3-2')


    def test_last_and_all_prevs(self):
        result = self.script.last_step()
        self.assertEqual(result, self.linear[-1])
        for times, expected in enumerate(reversed(self.linear[:-1]), start=1):
            with self.subTest(times=times, expected=expected):
                result = self.script.prev_step()
                self.assertEqual(result, expected)
        with self.assertRaises(ppytty.ScriptLimit):
            _ = self.script.prev_step()



# ----------------------------------------------------------------------------
