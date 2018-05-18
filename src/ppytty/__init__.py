# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
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


from . widgets import (
    SlideSequence, SlideSequenceKeyboard, SlideSequenceTimed,
    Slide,
    WidgetSequence, WidgetSequenceKeyboard, WidgetSequenceTimed,
    Label,
    Widget, Serial, Parallel, DelayReturn, KeyboardAction,
)
from . player import run
from . main import main

__all__ = [
    'SlideSequence',
    'SlideSequenceKeyboard',
    'SlideSequenceTimed',
    'Slide',
    'WidgetSequence',
    'WidgetSequenceKeyboard',
    'WidgetSequenceTimed',
    'Label',
    'Widget',
    'Serial',
    'Parallel',
    'DelayReturn',
    'KeyboardAction',
    'run',
    'main',
]


# ----------------------------------------------------------------------------
