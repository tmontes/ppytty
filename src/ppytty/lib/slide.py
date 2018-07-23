# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import thing



class Slide(thing.Thing):

    def __init__(self, title, **kw):

        super().__init__(id=title)

        self._title = title


    async def run(self):

        while True:
            sender, message = await api.message_wait()
            # sender assumed to be the parent, message will be one of:
            # - 'next', 'prev', 'cleanup'.
            self._log.warning('%s: got %r', self._title, message)
            await api.message_send(sender, 'ok')


# ----------------------------------------------------------------------------
