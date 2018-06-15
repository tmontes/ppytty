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



__version__ = '1.0.0a0'

__title__ = 'ppytty'
__description__ = 'ppytty'

__license__ = 'MIT'
__uri__ = 'https://github.com/tmontes/ppytty/'

__author__ = 'Tiago Montes'
__email__ = 'tiago.montes@gmail.com'


from . tasks import (
    Task,
    Parallel, Serial,
    DelayReturn, KeyboardAction, Loop,
    OuterSequenceKeyboard, OuterSequenceTimed,
    InnerSequenceKeyboard, InnerSequenceTimed,
)
from . widgets import (
    Slide,
    Label,
    Widget,
)
from . kernel import run

__all__ = [
    'OuterSequenceKeyboard',
    'OuterSequenceTimed',
    'Slide',
    'InnerSequenceKeyboard',
    'InnerSequenceTimed',
    'Label',
    'Widget',
    'Task',
    'Serial',
    'Parallel',
    'DelayReturn',
    'KeyboardAction',
    'Loop',
    'run',
]


# ----------------------------------------------------------------------------
