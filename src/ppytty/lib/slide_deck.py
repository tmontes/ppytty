# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import task
from . import key_reader



_DEFAULT_KEYMAP = {
    b']': 'slide-next',
    b'}': 'next',
    b'{': 'prev',
    b'r': 'reload',
}



class SlideDeck(task.Task):

    def __init__(self, slides, keymap=None, **kw):

        super().__init__(**kw)

        self._slides = slides
        self._current_index = None
        self._current_slide = None

        # False if we can tell it to go 'next'. True otherwise.
        self._slide_done = None

        # Passed to slides, so they can, for example, display these.
        self._context = {
            'slide_number': None,
            'slide_count': len(slides),
        }

        self._key_reader = key_reader.KeyReader()
        self._keymap = keymap if keymap else _DEFAULT_KEYMAP


    @property
    def context(self):

        self._context['slide_number'] = self._current_index + 1
        return self._context


    async def run(self):

        await api.task_spawn(self._key_reader)

        self._current_index = 0
        self._current_slide = self._slides[0]
        await self.launch_slide()

        while True:
            sender, message = await api.message_wait()
            self._log.debug('message from %r: %r', sender, message)
            if sender is self._key_reader:
                action = self._keymap.get(message)
                if action is None:
                    continue
                if action == 'slide-next':
                    if self._slide_done:
                        await self.navigate('next')
                    else:
                        await self.navigate_in_slide('next')
                else:
                    await self.navigate(action)
            elif sender is self._current_slide:
                # slide responded to 'next' with 'running'/'done'.
                self.update_navigation_from_response(message)
            else:
                self._log.error('unexpected sender=%r, message=%r', sender, message)

        await api.task_destroy(self._key_reader)
        await api.task_wait()


    async def navigate(self, action):

        delta_index = {'next': 1, 'prev': -1, 'reload': 0}
        new_index = self._current_index + delta_index.get(action, 0)
        if 0 <= new_index < len(self._slides):
            slide_to_cleanup = self._current_slide
            self._current_index = new_index
            self._current_slide = self._slides[new_index]
            await self.launch_slide(slide_to_cleanup)
        else:
            self._log.info('will not go to index %r', new_index)


    async def launch_slide(self, slide_to_cleanup=None):

        if slide_to_cleanup is not None:
            self._log.info('cleaning up %r', slide_to_cleanup)
            await slide_to_cleanup.cleanup('cleanup')
            self._log.info('cleaned up %r', slide_to_cleanup)

        slide_to_launch = self._current_slide

        self._log.info('launching %r', slide_to_launch)
        response = await slide_to_launch.launch(message='next', **self.context)
        self.update_navigation_from_response(response)
        self._log.info('launched %r done=%r', slide_to_launch, self._slide_done)


    def update_navigation_from_response(self, response):

        self._slide_done = (response == 'done')
        if response not in ('running', 'done'):
            self._log.warning('unexpected navigation response: %r', response)


    async def navigate_in_slide(self, request):

        destination = self._current_slide
        message = (request, self.context)
        self._log.debug('sending to %r: %r', destination, message)
        await api.message_send(destination, message)


# ----------------------------------------------------------------------------
