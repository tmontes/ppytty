# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run, TrapException

from . import helper_io



class TestParentToChild(helper_io.NoOutputTestCase):

    def _child(self, sleep_first):
        if sleep_first:
            yield ('sleep', 0)
        sender, message = yield ('message-wait',)
        return ('child tag', sender, message)


    def _parent(self, child_sleeps_first):
        child_task = self._child(child_sleeps_first)
        yield ('task-spawn', child_task)
        yield ('message-send', child_task, 'ping?')
        completed_task, child_success, child_result = yield ('task-wait',)
        return completed_task is child_task, child_success, child_result


    def test_parent_spawn_send_child_message_wait(self):

        # child_sleeps_first: parent message-send BEFORE child message-wait

        parent_task = self._parent(child_sleeps_first=True)
        success, result = run(parent_task)

        self.assertTrue(success)
        self._assert_parent_to_child_message_result(result, parent_task)


    def test_parent_spawn_child_message_wait_parent_send(self):

        # child_sleeps_first: parent message-send AFTER child message-wait

        parent_task = self._parent(child_sleeps_first=False)
        success, result = run(parent_task)

        self.assertTrue(success)
        self._assert_parent_to_child_message_result(result, parent_task)


    def _assert_parent_to_child_message_result(self, result, parent_task):

        waited_task_is_expeected, child_success, child_result = result
        self.assertTrue(waited_task_is_expeected)
        self.assertTrue(child_success)

        child_tag, child_message_sender, child_message_received = child_result
        self.assertEqual(child_tag, 'child tag')
        self.assertIs(child_message_sender, parent_task)
        self.assertEqual(child_message_received, 'ping?')



class TestChildToParent(helper_io.NoOutputTestCase):

    def _child(self, sleep_first):
        if sleep_first:
            yield ('sleep', 0)
        yield ('message-send', None, 'child-to-parent-message')
        return 'child-return-value'


    def _parent(self, child_sleeps_first):
        child_task = self._child(child_sleeps_first)
        yield ('task-spawn', child_task)
        sender_task, message = yield ('message-wait',)
        completed_task, child_success, child_result = yield ('task-wait',)
        return {
            'sender-task-correct': sender_task is child_task,
            'received-message': message,
            'completed-task-correct': completed_task is child_task,
            'child-success': child_success,
            'child-result': child_result,
        }


    def test_parent_spawn_message_wait_child_message_send(self):

        # child_sleeps_first: child message-send AFTER parent message-wait

        parent_task = self._parent(child_sleeps_first=True)
        success, result = run(parent_task)

        self.assertTrue(success)
        self._assert_child_to_parent_message_result(result, parent_task)


    def test_parent_spawn_child_message_send_parent_message_wait(self):

        # child_sleeps_first: child message-send BEFORE parent message-wait

        parent_task = self._parent(child_sleeps_first=False)
        success, result = run(parent_task)

        self.assertTrue(success)
        self._assert_child_to_parent_message_result(result, parent_task)


    def _assert_child_to_parent_message_result(self, result, parent_task):

        self.assertTrue(result['completed-task-correct'])
        self.assertTrue(result['child-success'])
        self.assertEqual(result['child-result'], 'child-return-value')

        self.assertTrue(result['sender-task-correct'])
        self.assertEqual(result['received-message'], 'child-to-parent-message')



class TestSenderTaskIsChildTask(helper_io.NoOutputTestCase):

    def _fast_child(self):

        yield ('message-send', None, 'hi-from-child')


    def _slow_child(self):

        yield ('sleep', 0)
        yield ('message-send', None, 'hi-from-child')


    def _parent(self, child_object):

        yield ('task-spawn', child_object)
        sender_task, message = yield ('message-wait',)
        completed_child, child_success, child_result = yield ('task-wait',)
        return sender_task, message, completed_child, child_success, child_result


    def _assert_parent_result(self, child_object, result):

        sender_task, message, completed_child, child_success, child_result = result
        self.assertIs(sender_task, child_object)
        self.assertEqual(message, 'hi-from-child')
        self.assertIs(completed_child, child_object)
        self.assertTrue(child_success)
        self.assertIsNone(child_result)


    def test_gen_function_child_parent_waits_1st(self):

        child_gen_function = self._slow_child
        parent = self._parent(child_gen_function)
        success, result = run(parent)
        self.assertTrue(success)
        self._assert_parent_result(child_gen_function, result)


    def test_gen_function_child_parent_waits_2nd(self):

        child_gen_function = self._fast_child
        parent = self._parent(child_gen_function)
        success, result = run(parent)
        self.assertTrue(success)
        self._assert_parent_result(child_gen_function, result)


    def test_gen_object_child_parent_waits_1st(self):

        child_gen_object = self._slow_child()
        parent = self._parent(child_gen_object)
        success, result = run(parent)
        self.assertTrue(success)
        self._assert_parent_result(child_gen_object, result)


    def test_gen_object_child_parent_waits_2nd(self):

        child_gen_object = self._fast_child()
        parent = self._parent(child_gen_object)
        success, result = run(parent)
        self.assertTrue(success)
        self._assert_parent_result(child_gen_object, result)



class TestTrapExceptions(helper_io.NoOutputTestCase):

    def test_top_task_message_parent_fails(self):

        def top_task():
            yield ('message-send', None, 'goes-nowhere')

        success, result = run(top_task)

        self.assertFalse(success)
        self.assertIsInstance(result, TrapException)
        self.assertGreaterEqual(len(result.args), 1)
        self.assertIn('parent', result.args[0])

# ----------------------------------------------------------------------------
