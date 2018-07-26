# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import widget



class Bullets(widget.Widget):

    def __init__(self, bullets, id=None, at_once=False, geometry=None, color=None):

        super().__init__(id=id, geometry=geometry, color=color)

        self._bullets = bullets
        self._bullet_count = len(bullets)

        self._at_once = at_once
        self._current_index = None


    @property
    def at_last_bullet(self):

        return self._current_index == self._bullet_count - 1


    async def handle_idle_next(self, **context):

        await super().handle_idle_next()

        if self._at_once:
            for bullet in self._bullets:
                self._log.warning('%s: bullet=%r context=%r', self, bullet, context)
            return 'done'

        self._current_index = 0
        bullet = self._bullets[0]
        self._log.warning('%s: bullet=%r context=%r', self, bullet, context)
        return 'done' if self.at_last_bullet else 'running'


    async def handle_running_next(self, **context):

        new_index = self._current_index + 1
        if new_index < self._bullet_count:
            bullet = self._bullets[new_index]
            self._current_index = new_index
            self._log.warning('%s: bullet=%r context=%r', self, bullet, context)
            return 'done' if self.at_last_bullet else 'running'
        else:
            return 'done'


    async def handle_cleanup(self, **kw):

        self._log.info('%s: nothing to cleanup, I guess', self)
        return await super().handle_cleanup(**kw)


# ----------------------------------------------------------------------------
