# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty.kernel import run, api, loop

from . import helper_io
from . import helper_log



class Test(helper_io.NoOutputAutoTimeControlledInputTestCase):

    def test_read_key(self):

        async def task():
            result = await api.key_read()
            return result

        self.input_control.feed_data(b'x')

        success, result = run(task)

        self.assertTrue(success)
        self.assertEqual(result, b'x')


    def test_blocking_read_key(self):

        async def child():
            byte_key = await api.key_read()
            return byte_key

        async def parent(child_task):
            await api.task_spawn(child_task)
            await api.sleep(1)
            self.input_control.feed_data(b'k')
            task_wait_result = await api.task_wait()
            return task_wait_result

        child_task = child()
        success, result = run(parent(child_task))

        self.assertTrue(success)

        completed_task, child_success, child_result = result
        self.assertIs(completed_task, child_task)
        self.assertTrue(child_success)
        self.assertEqual(child_result, b'k')


    def test_put_key(self):

        async def first_reader_child():
            byte_key = await api.key_read()
            await api.key_unread(byte_key)
            await api.sleep(42)

        async def second_reader_child():
            byte_key = await api.key_read()
            return byte_key

        async def parent(first_reader, second_reader):
            all_tasks = {first_reader, second_reader}
            await api.task_spawn(first_reader)
            await api.task_spawn(second_reader)
            await api.sleep(1)
            self.input_control.feed_data(b't')
            completed_task, child_success, child_result = await api.task_wait()
            all_tasks.remove(completed_task)
            other_task = all_tasks.pop()
            await api.task_destroy(other_task)
            destroyed_task, _, _ = await api.task_wait()
            return completed_task, child_success, child_result, destroyed_task

        success, result = run(parent(first_reader_child, second_reader_child))

        self.assertTrue(success)
        completed_task, child_success, child_result, destroyed_task = result
        self.assertIs(completed_task, second_reader_child)
        self.assertTrue(child_success)
        self.assertEqual(child_result, b't')
        self.assertIs(destroyed_task, first_reader_child)


    def test_kernel_run_stops_with_double_q_input(self):

        async def task():
            self.input_control.feed_data(b'qq')
            while True:
                await api.sleep(42)

        success, result = run(task)

        self.assertIsNone(success)
        self.assertIsInstance(result, loop._ForcedStop)


    def test_kernel_run_does_not_stop_with_q_and_something_else(self):

        async def task():
            await api.sleep(42)
            return 'confirming-regular-completion'

        self.input_control.feed_data(b'qx')

        success, result = run(task)

        self.assertTrue(success)
        self.assertNotIsInstance(result, loop._ForcedStop)
        self.assertEqual(result, 'confirming-regular-completion')


    def test_kernel_run_dumps_state_with_capital_d_input(self):

        async def task():
            await api.sleep(1)

        log_handler = helper_log.create_and_add_handler()
        self.addCleanup(lambda: helper_log.remove_handler(log_handler))

        self.input_control.feed_data(b'D')

        success, result = run(task)

        self.assertTrue(success)
        self.assertIsNone(result)

        separator_line_count = sum(
            1 for msg in log_handler.messages
            if 'DUMP STATE' in msg
        )
        self.assertGreaterEqual(separator_line_count, 1)


# ----------------------------------------------------------------------------
