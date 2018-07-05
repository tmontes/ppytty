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


    def test_single_window_print_and_render(self):

        def task():
            w = yield ('window-create', 0, 0, 40, 20)
            w.print('text-in-the-window')
            yield ('window-render', w)
            yield ('window-destroy', w)

        success, result = run(task)
        self.assertTrue(success)
        self.assertIsNone(result)

        # Very simplified test: our window printed string was os.written.
        written_bytes = self.get_os_written_bytes()
        self.assertIn(b'text-in-the-window ', written_bytes)


    def test_complex_windows_print_and_render(self):

        #   top_win
        #   +-----------------------+                     oth_win
        #   |(0, 0)                 | bot_win   +---------------+
        #   |       +-  -  -  -  -  |-------+   |(50,3)         |
        #   |       .(10, 5)        |       |   |               |
        #   |       .               |       |   +---------------+
        #   +-----------------------+       |
        #           |                       |
        #           +-----------------------+

        def task():
            # created first to exercise rendering optimizations
            oth_win = yield ('window-create', 50, 3, 20, 5)
            oth_win.print('oth-win-frst-line', 0, 0)
            oth_win.print('oth-win-last-line', 0, 4)

            bot_win = yield ('window-create', 10, 5, 30, 10)
            bot_win.print('bot-win-frst-line', 0, 0)
            bot_win.print('bot-win-last-line', 0, 9)

            top_win = yield ('window-create', 0, 0, 30, 10)
            top_win.print('top-win-frst-line', 0, 0)
            top_win.print('top-win-last-line', 0, 9)

            # top_win and bot_win must overlap
            if not top_win.overlaps(bot_win):
                return False, 'top_win/bot_win do not overlap'

            # rendering bot_win forces the overlapped top_win to render as well
            yield ('window-render', bot_win)

            # rendering pseudo-assertions
            written_bytes = self.get_os_written_bytes()
            if b'bot-win-frst-line' in written_bytes:
                return False, 'bot-win-frst-line should not be rendered'
            for expected_render in (b'bot-win-last-line', b'top-win-frst-line',
                                    b'top-win-last-line',):
                if expected_render not in written_bytes:
                    return False, f'{expected_render} not rendered'

            # go for the non-overlapping window checks
            if oth_win.overlaps(top_win):
                return False, 'oth_win/top_win overlap'
            if oth_win.overlaps(bot_win):
                return False, 'oth_win/bot_win overlap'

            # clear os_written bytes in preparation for another render test
            self.reset_os_written_bytes()

            # rendering oth_win should not re-render the other windows:
            # even though they are on top, they do not overlap
            yield ('window-render', oth_win)

            # rendering pseudo-assertions
            written_bytes = self.get_os_written_bytes()
            for expected_render in (b'oth-win-frst-line', b'oth-win-last-line',):
                if expected_render not in written_bytes:
                    return False, f'{expected_render} not rendered'
            for not_there in (b'bot-win-frst-line', b'bot-win-last-line',
                              b'top-win-frst-line', b'top-win-last-line',):
                if not_there in written_bytes:
                    return False, f'{not_there} should not be rendered'

            return True, None

        success, result = run(task)
        self.assertTrue(success)

        pseudo_asserts_ok, failure_msg = result
        self.assertTrue(pseudo_asserts_ok, failure_msg)


    def test_task_termination_forces_all_other_windows_render(self):

        def child():
            w = yield ('window-create', 40, 0, 30, 10)
            yield ('window-render', w)
            yield ('message-send', None, 'child-rendered')
            yield ('message-wait',)

        def parent():
            # setup our window
            w = yield ('window-create', 0, 0, 30, 10)
            w.print('parent-window-frst-line', 0, 0)
            w.print('parent-window-last-line', 0, 9)
            yield ('window-render', w)

            # child will create a window and let parent know when it's rendered
            yield ('task-spawn', child)
            yield ('message-wait',)

            # reset os written bytes and send message so that child terminates
            self.reset_os_written_bytes()
            yield ('message-send', child, 'you-can-terminate')
            yield ('task-wait',)

            # caller will assert that os written bytes include our window
            return self.get_os_written_bytes()

        success, written_bytes = run(parent)

        self.assertTrue(success)
        self.assertIn(b'parent-window-frst-line', written_bytes)
        self.assertIn(b'parent-window-last-line', written_bytes)


# ----------------------------------------------------------------------------
