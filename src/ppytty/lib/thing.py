# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


from ppytty.kernel import api

from . import task



class Thing(task.Task):

    # Things have a simple lifecycle:
    # - They start in the 'idle' state.
    # - They loop waiting for request messages.
    # - Messages are handled via method lookup:
    #   - First a method named "handle_{state}_{request}" is looked up.
    #   - If not found, "handle_{request}" is tried.
    #   - If not found, "default_handler" is used.
    # - Successfully handled request messages must be responded to with 'ok'.
    # - Successful handling of a request while 'idle', changes the state to 'running'.
    # - One particular message is handled successfully: 'cleanup'.
    # - Once responded to, the thing (as a Task) terminates.

    def __init__(self, **kw):

        super().__init__(**kw)

        # One of 'idle', 'running', or 'completed'.
        self._state = 'idle'


    def reset(self):

        super().reset()
        self._state = 'idle'


    async def run(self):

        self._log.warning('%r: started', self)

        while self._state != 'completed':
            sender, request = await api.message_wait()
            self._log.warning('%s: got request: %r', self, request)
            handler = self.get_handler(request)
            try:
                response = await handler(request)
            except Exception:
                self._log.error('handler exception', exc_info=True)
                response = 'fail'
            if self._state == 'idle' and response == 'ok':
                self._state = 'running'
            await api.message_send(sender, response)

        self._log.warning('%r: done', self)


    def get_handler(self, request):

        handler_name = f'handle_{self._state}_{request}'
        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            handler_name = f'handle_{request}'
            handler = getattr(self, handler_name, self.default_handler)
        return handler


    def im_done(self):

        self._state = 'completed'


    async def handle_cleanup(self, _request):

        self.im_done()
        return 'ok'


    async def default_handler(self, request):

        raise NotImplementedError()


# ----------------------------------------------------------------------------
