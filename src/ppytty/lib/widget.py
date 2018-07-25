# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import thing



class Widget(thing.Thing):

    async def handle_idle_next(self, **_kw):

        self._log.info('%s: create window', self)
        return 'done'


    async def handle_cleanup(self, **_kw):

        self._log.info('%s: destroy window (in deferred mode)', self)
        return await super().handle_cleanup()



# ----------------------------------------------------------------------------
