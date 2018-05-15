# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import sys

import ppytty


def main():

    print(f'{ppytty.__name__} {ppytty.__version__}')
    print(f'sys.argv[1:]={sys.argv[1:]!r}')
    script = ppytty.Script([
        [
            (None, 0, 'print', '1 first script entry'),
            (None, 0, 'print', '1 second script entry'),
        ],
        [
            (None, 0, 'print', '2 third script entry'),
            (None, 0, 'wait', None,),
            (None, 0, 'print', '2 fourth script entry'),
        ],
        [
            (None, 0, 'print', '3 last script entry'),
        ],
    ])
    player = ppytty.Player(script)
    player.run()
    print('main is done')
    return 42

# ----------------------------------------------------------------------------
