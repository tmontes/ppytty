# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import logging
import os
import sys

import ppytty


def main():

    print(f'{ppytty.__name__} {ppytty.__version__}')
    print(f'sys.argv[1:]={sys.argv[1:]!r}')

    log_filename = os.environ.get('PPYTTY')
    if log_filename:
        logging.basicConfig(
            filename=log_filename,
            format='%(asctime)s %(levelname).1s %(name)s %(message)s',
            datefmt='%H:%M:%S',
            level=logging.INFO,
        )
        
    log = logging.getLogger('ppytty')
    log.info('started')

    widget = ppytty.SlideDeck([
        ppytty.Slide([
            ppytty.Label('Hello world!', name='l1'),
            ppytty.Label('And more...', name='l2'),
        ], name='s1'),
        ppytty.Slide([
            ppytty.Label('...nearly done', name='l3'),
        ], name='s2')
    ])
    player = ppytty.Player(widget)
    player.run()

    print('main is done')
    log.info('done')
    return 42


if __name__ == '__main__':
    main()

# ----------------------------------------------------------------------------
