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
        self._slide_count = len(slides)
        self._current_index = None
        self._current_slide = None

        self._slide_request = None
        self._slide_next_ok = None

        self._key_reader = key_reader.KeyReader()
        self._keymap = keymap if keymap else _DEFAULT_KEYMAP


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
                    if not self._slide_next_ok:
                        await self.navigate('next')
                    else:
                        self._slide_request = 'next'
                        await self.message_send()
                else:
                    await self.navigate(action)
            elif sender is self._current_slide:
                # slide responded to 'next' with 'ok'/'done'.
                self.update_navigation_from_response(message)
            else:
                self.log_unexpected_sender(sender, message)

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
            response = await self.message_send_receive(slide_to_cleanup, 'cleanup')
            if response != 'ok':
                self._log.error('could not cleanup previous slide')
            self._log.debug('waiting for %r termination', slide_to_cleanup)
            terminated, _, _ = await api.task_wait()
            if terminated is not slide_to_cleanup:
                self._log.error('unexpected child terminated: %r', terminated)
            terminated.reset()
            self._log.debug('previous slide cleaned up')

        self._log.info('spawning slide: %r', self._current_slide)
        await api.task_spawn(self._current_slide)

        self._slide_request = 'next'
        response = await self.message_send_receive()
        self._log.info('spawned slide response: %r', response)

        self._slide_next_ok = False
        self.update_navigation_from_response(response)


    def update_navigation_from_response(self, response):

        if self._slide_request == 'next':
            self._slide_next_ok = (response == 'ok')
            if response not in ('ok', 'done'):
                self._log.warning('unexpected response: %r', response)
        self._log.debug('slide navigation: next_ok=%r', self._slide_next_ok)


    async def message_send(self, destination=None, request=None):

        if destination is None:
            destination = self._current_slide
        if request is None:
            request = self._slide_request
        message = (request, {
            'slide_number': self._current_index+1,
            'slide_count': self._slide_count,
        })
        self._log.debug('sending to %r: %r', destination, message)
        await api.message_send(destination, message)
        return destination


    async def message_send_receive(self, destination=None, request=None):

        destination = await self.message_send(destination, request)
        sender, response = await api.message_wait()
        self._log.debug('response from %r: %r', sender, response)
        if sender is not destination:
            self.log_unexpected_sender(sender, response)
        return response


    def log_unexpected_sender(self, sender, message):

        self._log.error('unexpected sender=%r, message=%r', sender, message)


# ----------------------------------------------------------------------------
