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
    b'[': 'slide-prev',
    b'}': 'next',
    b'{': 'prev',
    b'r': 'reload',
}


class SlideDeck(task.Task):

    def __init__(self, slides, keymap=None, **kw):

        super().__init__(**kw)

        self._slides = slides
        self._current_slide = None
        self._current_index = None

        self._slide_request = None
        self._slide_next_ok = None
        self._slide_prev_ok = None

        self._key_reader = key_reader.KeyReader()
        self._keymap = keymap if keymap else _DEFAULT_KEYMAP


    async def run(self):

        await api.task_spawn(self._key_reader)

        self._current_index = 0
        self._current_slide = self._slides[0]
        await self.launch_slide()

        while True:
            self._log.warning('index=%r slide_next=%r slide_prev=%r',
                              self._current_index, self._slide_next_ok,
                              self._slide_prev_ok)
            sender, message = await api.message_wait()
            if sender is self._key_reader:
                action = self._keymap.get(message)
                if action is None:
                    continue
                self._log.warning('action=%r', action)
                if action.startswith('slide-'):
                    slide_request = action[6:]
                    if ((slide_request == 'next' and not self._slide_next_ok) or
                        (slide_request == 'prev' and not self._slide_prev_ok)):
                        await self.navigate(slide_request)
                    else:
                        self._slide_request = slide_request
                        await self.message_send()
                else:
                    await self.navigate(action)
            elif sender is self._current_slide:
                # slide responded to 'next'/'prev' with 'ok'/'done'.
                self._log.warning('slide says: %r', message)
                self.update_navigation_from_response(message)
            else:
                self.log_unexpected_sender(sender, message)

        await api.task_destroy(self._key_reader)
        await api.task_wait()


    async def navigate(self, action):

        delta_index = {'next': 1, 'prev': -1, 'reload': 0}
        new_index = self._current_index + delta_index.get(action, 0)
        if 0 <= new_index < len(self._slides):
            prev_slide = self._current_slide
            self._current_index = new_index
            self._current_slide = self._slides[new_index]
            await self.launch_slide(prev_slide)
        else:
            self._log.warning('will not go to index %r', new_index)


    async def launch_slide(self, prev_slide=None):

        if prev_slide is not None:
            response = await self.message_send_receive(prev_slide, 'cleanup')
            if response != 'ok':
                self._log.error('could not cleanup previous slide')
            terminated, _, _ = await api.task_wait()
            if terminated is not prev_slide:
                self._log.error('unexpected child terminated: %r', terminated)
            terminated.reset()

        self._log.warning('spawning slide: %r', self._current_slide)
        await api.task_spawn(self._current_slide)

        self._slide_request = 'next'
        response = await self.message_send_receive()
        self._log.warning('slide response: %r', response)

        self._slide_next_ok = False
        self._slide_prev_ok = False
        self.update_navigation_from_response(response)


    def update_navigation_from_response(self, response):

        if self._slide_request == 'next':
            self._slide_next_ok = (response == 'ok')
            if response not in ('ok', 'done'):
                self._log.warning('unexpected response: %r', response)
        elif self._slide_request == 'prev':
            self._slide_prev_ok = (response == 'ok')
            if response not in ('ok', 'done'):
                self._log.warning('unexpected response: %r', response)


    async def message_send(self, destination=None, request=None):

        if destination is None:
            destination = self._current_slide
        if request is None:
            request = self._slide_request
        await api.message_send(destination, request)
        return destination


    async def message_send_receive(self, destination=None, request=None):

        destination = await self.message_send(destination, request)
        sender, response = await api.message_wait()
        if sender is not destination:
            self.log_unexpected_sender(sender, response)
        return response


    def log_unexpected_sender(self, sender, message):

        self._log.error('unexpected sender=%r, message=%r', sender, message)


# ----------------------------------------------------------------------------
