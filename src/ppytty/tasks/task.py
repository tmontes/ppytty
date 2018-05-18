# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


import logging



class Task(object):

    def __init__(self, name=None):

        self._name = name
        self._running = None

        self._log = logging.getLogger(f'task.{self._name}')


    def __repr__(self):

        name = repr(self._name) if self._name else f'at {hex(id(self))}'
        return f'<{self.__class__.__name__} {name}>'


    @property
    def running(self):

        if self._running is None:
            self._running = self.run()

        return self._running


    def run(self):

        raise NotImplementedError()


    def reset(self):

        self._running = None


# ----------------------------------------------------------------------------
