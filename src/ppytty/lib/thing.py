# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import task



class Thing(task.Task):

    # Things are Tasks that track state and process messages:
    # - State is defined by a string.
    # - They loop waiting for request messages.
    # - Messages are handled via method lookup:
    #   - First a method named "handle_{state}_{request}" is looked up.
    #   - If not found, "handle_{request}" is tried.
    #   - If not found, "default_handler" is used.
    # - Handlers should return a string:
    #   - This updates the state...
    #   - ...which is sent back to message senders.
    # - They terminate once:
    #   - The `im_done` method is called and...
    #   - ...they receive a message, to support termination synchronization.

    def __init__(self, id=None, initial_state=None):

        super().__init__(id=id)

        self._initial_state = initial_state
        self._state = self._initial_state

        self._last_sender = None
        self._done = False


    @property
    def controller(self):

        return self._last_sender


    def reset(self):

        super().reset()
        self._state = self._initial_state
        self._done = False


    async def run(self):

        self._log.info('started')

        while not self._done:
            self._last_sender, message = await api.message_wait()
            self._log.debug('got message: %r', message)
            request, request_args = message
            handler = self.get_handler(request)
            try:
                new_state = await handler(**request_args)
            except Exception:
                self._log.error('handler exception', exc_info=True)
            else:
                self._state = new_state
            await api.message_send(self._last_sender, new_state)

        # Synchronize Task termination: wait for a message that should be `None`.
        _, message = await api.message_wait()
        if message is not None:
            self._log.warning('unexpected exit confirmation: %r', message)

        self._log.info('done')


    def get_handler(self, request):

        handler_name = f'handle_{self._state}_{request}'
        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            handler_name = f'handle_{request}'
            handler = getattr(self, handler_name, self.default_handler)
        return handler


    def im_done(self):

        self._done = True


    async def default_handler(self, **_kw):

        raise NotImplementedError()


# ----------------------------------------------------------------------------
