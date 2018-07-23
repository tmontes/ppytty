# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import thing
from . import key_reader



_DEFAULT_KEYMAP = {
    b']': 'child-next',
    b'[': 'child-prev',
    b'}': 'next',
    b'{': 'prev',
    b'r': 'reload',
}


class SlideDeck(thing.Thing):

    def __init__(self, slides, keymap=None, **kw):

        super().__init__(**kw)

        self._slides = slides
        self._current_slide = None

        self._key_reader = key_reader.KeyReader()
        self._keymap = keymap if keymap else _DEFAULT_KEYMAP


    async def run(self):

        await api.task_spawn(self._key_reader)

        self._current_slide = self._slides[0]
        await api.task_spawn(self._current_slide)

        while True:
            sender, message = await api.message_wait()
            if sender is self._key_reader:
                action = self._keymap.get(message)
                if action is None:
                    continue
                self._log.warning('action=%r', action)
                if action.startswith('child-'):
                    await api.message_send(self._current_slide, action[6:])
                else:
                    # next/prev/reload slide:
                    # - send 'cleanup' to current_slide
                    # - wait for current_slide termination
                    # - reset current_slide (so it's read for next time)
                    # - update current_slide to point where it should
                    # - spawn current_slide
                    # - send 'next' current_slide
                    pass
            elif sender is self._current_slide:
                # slide responded to request message:
                # - one of 'next', 'prev'
                self._log.warning('slide says: %r', message)
            else:
                self._log.error('unknown sender=%r, msg=%r', sender, message)

        await api.task_destroy(self._key_reader)
        await api.task_wait()


# ----------------------------------------------------------------------------
