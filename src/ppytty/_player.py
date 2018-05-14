# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

from . _terminal import Terminal


class Player(object):

    def __init__(self, script):
        self._script = script

    def run(self):
        with Terminal() as terminal:
            for entry in self._script:
                terminal.print(entry)

# ----------------------------------------------------------------------------
