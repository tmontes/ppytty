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

        logger_name_parts = __name__.split('.')[:-1]
        logger_name_parts.append(type(self).__qualname__)
        self._log = logging.getLogger('.'.join(logger_name_parts))


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
