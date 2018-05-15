# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------



class Script(object):

    def __init__(self, steps):

        self._steps = steps
        self._max_step_index = len(steps) - 1

        self._current_step_index = 0


    def current_step(self):

        return self._steps[self._current_step_index]


    def next_step(self):

        if self._current_step_index == self._max_step_index:
            raise ValueError()

        self._current_step_index += 1
        return self.current_step()


    def prev_step(self):

        if self._current_step_index == 0:
            raise ValueError()

        self._current_step_index -= 1
        return self.current_step()


    def first_step(self):

        self._current_step_index = 0
        return self.current_step()


    def last_step(self):

        self._current_step_index = self._max_step_index
        return self.current_step()


# ----------------------------------------------------------------------------