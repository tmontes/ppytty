# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty import run

from . import io_bypass
from . import log_helper



class Test(io_bypass.NoOutputTestCase):

    def test_parent_to_child_message_send_wait(self):

        def child():
            sender, message = yield ('message-wait',)
            return ('child return is', sender, message)

        def parent():
            child_task = child()
            yield ('task-spawn', child_task)
            yield ('message-send', child, 'ping?')
            result = yield ('task-wait',)
            return result

        x = run(parent)
        self.assertEqual(x, 'sopa')


# ----------------------------------------------------------------------------
