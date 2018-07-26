# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import task



class Thing(task.Task):

    # Things track state and process messages:
    # - State is defined by a string.
    # - They loop waiting for request messages.
    # - Messages are handled via method lookup:
    #   - First a method named "handle_{state}_{request}" is looked up.
    #   - If not found, "handle_{request}" is tried.
    #   - If not found, "default_handler" is used.
    # - Handlers should return a string:
    #   - This updates the state...
    #   - ...which is sent back to message senders.

    def __init__(self, id=None, initial_state=None):

        super().__init__(id=id)

        self._initial_state = initial_state
        self._state = self._initial_state

        self._done = False


    def reset(self):

        super().reset()
        self._state = self._initial_state
        self._done = False


    async def run(self):

        self._log.info('%r: started', self)

        while not self._done:
            sender, message = await api.message_wait()
            self._log.debug('%s: got message: %r', self, message)
            request, request_args = message
            handler = self.get_handler(request)
            try:
                new_state = await handler(**request_args)
            except Exception:
                self._log.error('handler exception', exc_info=True)
            else:
                self._state = new_state
            await api.message_send(sender, new_state)

        self._log.info('%r: done', self)


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


    # ------------------------------------------------------------------------
    # To be used by others to launch me/clean me up.

    async def launch(self, message, until_state=None, **kw):

        await api.task_spawn(self)
        message = (message, kw)
        done = False
        while not done:
            await api.message_send(self, message)
            sender, reached_state = await api.message_wait()
            if sender is not self:
                self.log_unexpected_sender(sender, reached_state)
            if until_state is None or until_state == reached_state:
                done = True
        return reached_state


    async def cleanup(self, message, **kw):

        message = (message, kw)
        await api.message_send(self, message)
        sender, cleanup_response = await api.message_wait()
        if sender is not self:
            self.log_unexpected_sender(sender, cleanup_response)
        if cleanup_response is not None:
            self._log.warning('%r: unexpected cleanup response: %r', self, cleanup_response)
        completed, _, _ = await api.task_wait()
        if completed is not self:
            self._log.warning('%r: unexpected child terminated: %r', self, completed)
        self.reset()


    def log_unexpected_sender(self, sender, response):

        self._log.warning('%s: unexpected sender=%r response=%r', self, sender, response)


# ----------------------------------------------------------------------------
