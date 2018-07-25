# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api
from . import task



class KeyReader(task.Task):

    async def run(self):

        while True:
            keyboard_bytes = await api.key_read()
            await api.message_send(None, keyboard_bytes)


# ----------------------------------------------------------------------------
