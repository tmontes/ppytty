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

        logger_name = f'ppytty.task.{self.__class__.__name__}.{self._name}'
        self._log = logging.getLogger(logger_name)


    def __repr__(self):

        name = f' {self._name!r}' if self._name else ''
        return f'<{self.__class__.__name__}{name} {hex(id(self))}>'


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
