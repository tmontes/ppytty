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
            (None, 0, 'clear', None),
            (None, 0, 'print', '1-1 first script entry'),
            (None, 0, 'print', '1-2 second script entry'),
        ],
        ppytty.Script([
            [
                (None, 0, 'clear', None),
                (None, 0, 'print', '2-1 third script entry'),
            ], [
                (None, 0, 'print', '2-2 fourth script entry'),
                (None, 0, 'print', '2-3 fourth script entry'),
            ],
        ]),
        ppytty.Script([
            [
                (None, 0, 'clear', None),
                (None, 0, 'print', '3-1 penultimate script entry'),
            ], [
                (None, 0, 'print', '3-2 last script entry'),
            ],
        ])
    ])
    player = ppytty.Player(script)
    player.run()
    print('main is done')
    return 42

# ----------------------------------------------------------------------------
