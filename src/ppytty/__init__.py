# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
ppytty
"""

from __future__ import absolute_import

import logging


# Prevent logs from going anywhere, when logging is not configured.
# See https://docs.python.org/3/howto/logging.html#library-config.
logging.getLogger('ppytty').addHandler(logging.NullHandler())


__version__ = '1.0.0a0'

__title__ = 'ppytty'
__description__ = 'ppytty'

__license__ = 'MIT'
__uri__ = 'https://github.com/tmontes/ppytty/'

__author__ = 'Tiago Montes'
__email__ = 'tiago.montes@gmail.com'



from . kernel import run

from . lib import *


__all__ = [
    'run',
    'SlideDeck',
    'Slide',
]

# ----------------------------------------------------------------------------
