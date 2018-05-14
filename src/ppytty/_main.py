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
        (0, 'print', 'first \N{SMILING FACE WITH SMILING EYES}  script entry'),
        (0, 'wait', None,),
        (0, 'print', 'last script entry'),
    ]
    ppytty.run(script)
    print('main is done')
    return 42

# ----------------------------------------------------------------------------
