# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run, TrapException
from ppytty.kernel import window
from ppytty.kernel.state import state

from . import io_bypass



class Test(io_bypass.NoOutputTestCase):

    def test_window_create_returns_a_window(self):

        def task():
            w = yield ('window-create', 0, 0, 40, 20)
            is_window_instance = isinstance(w, window.Window)
            return is_window_instance

        success, result = run(task)
        self.assertTrue(success)
        self.assertTrue(result, 'window-create returned non-Window object')


    def test_window_destroy_raises_with_bad_argument(self):

        def task():
            non_window_object = 42
            yield ('window-destroy', non_window_object)

        success, result = run(task)
        self.assertFalse(success)
        self.assertIsInstance(result, TrapException)
        # "window" somewhere inside the exceptions "message"
        self.assertIn('window', result.args[0])


    def test_window_create_and_destroy(self):

        def task():
            w = yield ('window-create', 0, 0, 40, 20)
            yield ('window-destroy', w)

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)


    def test_task_windows_destroyed_on_task_completion(self):

        def child():
            w = yield ('window-create', 0, 0, 40, 20)
            window_in_state = w in state.all_windows
            return window_in_state

        def parent():
            yield ('task-spawn', child)
            _, child_success, window_in_state = yield ('task-wait',)
            window_cleared = len(state.all_windows) == 0
            return child_success, window_in_state, window_cleared

        success, result = run(parent)
        self.assertTrue(success)
        child_success, window_in_state, window_cleared = result

        self.assertTrue(child_success)
        self.assertTrue(window_in_state)
        self.assertTrue(window_cleared)


    def test_task_windows_destroyed_on_task_exception(self):

        def child():
            w = yield ('window-create', 0, 0, 40, 20)
            window_in_state = w in state.all_windows
            raise RuntimeError(window_in_state)

        def parent():
            yield ('task-spawn', child)
            _, child_success, child_exception = yield ('task-wait',)
            window_cleared = len(state.all_windows) == 0
            return child_success, child_exception, window_cleared

        success, result = run(parent)
        self.assertTrue(success)
        child_success, child_exception, window_cleared = result

        self.assertFalse(child_success)
        self.assertIsInstance(child_exception, RuntimeError)
        window_in_state = child_exception.args[0]
        self.assertTrue(window_in_state)
        self.assertTrue(window_cleared)


    def test_window_render_raises_with_bad_argument(self):

        def task():
            non_window_object = 42
            yield ('window-render', non_window_object)

        success, result = run(task)
        self.assertFalse(success)
        self.assertIsInstance(result, TrapException)
        # "window" somewhere inside the exceptions "message"
        self.assertIn('window', result.args[0])


# ----------------------------------------------------------------------------
