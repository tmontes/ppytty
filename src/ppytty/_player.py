# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

from . _terminal import Terminal


def run(script):

    with Terminal() as terminal:
        for _when, action, *args in script:
            if action == 'print':
                terminal.print(*args)
            elif action == 'wait':
                input('WAIT...')
            else:
                raise ValueError(f'unknown action {action!r}')
        input('PLAY: done')

# ----------------------------------------------------------------------------
