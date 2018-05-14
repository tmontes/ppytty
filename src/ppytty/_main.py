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
    script = [
        'first script entry',
        'last script entry',
    ]
    player = ppytty.Player(script)
    player.run()
    print('main is done')
    return 42

# ----------------------------------------------------------------------------
