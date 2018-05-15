# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------



class ScriptLimit(Exception):
    pass



class Script(object):

    def __init__(self, steps, name=None):

        self._name = repr(name) if name else hex(id(self))
        self._steps = steps
        self._max_step_index = len(steps) - 1

        self._current_step_index = 0


    def __repr__(self):

        return f'<Script {self._name}>'


    def _current_local_step(self):

        return self._steps[self._current_step_index]


    def first_sub_step(self):

        self._current_step_index = 0
        step = self._current_local_step()
        return step.first_sub_step() if isinstance(step, Script) else step


    def last_sub_step(self):

        self._current_step_index = self._max_step_index
        step = self._current_local_step()
        return step.last_sub_step() if isinstance(step, Script) else step


    def current_step(self):

        step = self._current_local_step()
        return step.current_step() if isinstance(step, Script) else step


    def next_sub_step(self, recurse=True):

        step = self._current_local_step()
        if recurse and isinstance(step, Script):
            try:
                return step.next_sub_step()
            except ScriptLimit:
                pass

        if self._current_step_index == self._max_step_index:
            raise ScriptLimit()

        self._current_step_index += 1
        step = self._current_local_step()
        return step.first_sub_step() if isinstance(step, Script) else step


    def prev_sub_step(self, recurse=True):

        step = self._current_local_step()
        if recurse and isinstance(step, Script):
            try:
                return step.prev_sub_step()
            except ScriptLimit:
                pass

        if self._current_step_index == 0:
            raise ScriptLimit()

        self._current_step_index -= 1
        step = self._current_local_step()
        return step.first_sub_step() if isinstance(step, Script) else step


    def first_step(self):

        return self.first_sub_step()


    def last_step(self):

        self._current_step_index = self._max_step_index
        step = self._current_local_step()
        return step.first_sub_step() if isinstance(step, Script) else step


    def prev_step(self):

        return self.prev_sub_step(recurse=False)


    def next_step(self):

        return self.next_sub_step(recurse=False)


# ----------------------------------------------------------------------------