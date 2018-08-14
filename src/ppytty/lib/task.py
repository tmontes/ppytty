# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import logging



class Task(object):

    def __init__(self, id=None):

        self._id = id
        self._running = None

        logger_name = f'{type(self).__module__}.{self!r}'
        self._log = logging.getLogger(logger_name)

    def __repr__(self):

        me = repr(self._id) if self._id else hex(id(self))
        return f'<{self.__class__.__name__} {me}>'


    def __call__(self):

        if self._running is None:
            self._running = self.run()
        return self


    def __getattr__(self, attr):

        return getattr(self._running, attr)


    def reset(self):

        self._running = None


    async def run(self):

        raise NotImplementedError()


# ----------------------------------------------------------------------------
