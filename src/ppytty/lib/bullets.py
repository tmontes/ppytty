# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget



class Bullets(widget.Widget):

    def __init__(self, bullets, **kw):

        super().__init__()

        self._bullets = bullets
        self._bullet_count = len(bullets)
        self._current_index = None


    @property
    def at_last_bullet(self):

        return self._current_index == self._bullet_count - 1


    async def handle_idle_next(self, **context):

        await super().handle_idle_next()

        self._current_index = 0
        bullet = self._bullets[0]

        self._log.warning('%s: bullet=%r context=%r', self, bullet, context)

        return 'done' if self.at_last_bullet else 'ok'


    async def handle_running_next(self, **context):

        new_index = self._current_index + 1
        if new_index < self._bullet_count:
            bullet = self._bullets[new_index]
            self._current_index = new_index
            self._log.warning('%s: bullet=%r context=%r', self, bullet, context)
            return 'done' if self.at_last_bullet else 'ok'
        else:
            return 'done'


    async def handle_cleanup(self, **_kw):

        self._log.info('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup()


# ----------------------------------------------------------------------------
