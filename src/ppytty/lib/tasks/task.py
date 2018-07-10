# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


import logging



class Task(object):

    # Kernel loop runs either generator functions or generator objects.
    # When given a callable, it will call it, and use the result as a generator
    # object, with its .send method to make it progress.
    #
    # Task behaves (enough) like a generator function in the sense that it is
    # callable. It also supports resetting itself, this the self._running
    # related complexity.

    def __init__(self, name=None):

        self._name = name
        self._running = None

        logger_name = f'ppytty.task.{self.__class__.__name__}.{self._name}'
        self._log = logging.getLogger(logger_name)


    def __repr__(self):

        name = f' {self._name!r}' if self._name else ''
        return f'<{self.__class__.__name__}{name} {hex(id(self))}>'


    def _start_running(self):

        self._running = self.run()


    def __call__(self):

        self._start_running()
        return self


    def send(self, *args, **kwargs):

        # The kernel loop calls this to make the Task progress.

        if self._running is None:
            self._start_running()

        return self._running.send(*args, **kwargs)


    def run(self):

        raise NotImplementedError()


    def reset(self):

        # TODO: Do we really need resettable Tasks? TBD, as the lib evolves.
        self._running = None


# ----------------------------------------------------------------------------
