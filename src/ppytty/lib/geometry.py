# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
geometry.py

Helper functions returning dicts with geometry information for Widgets.
"""


def _geometry_dict(x=0, y=0, w=1.0, h=1.0, dx=0, dy=0, dw=0, dh=0):

    return dict(x=x, y=y, w=w, h=h, dx=dx, dy=dy, dw=dw, dh=dh)



def full():

    return _geometry_dict()



def horizontal_bar(height, from_top=True, margin=0, dx=0, dw=0):

    y = 0 if from_top else -height
    dy = margin if from_top else -margin
    return _geometry_dict(y=y, h=height, dx=dx, dy=dy, dw=dw)



def vertical_bar(width, from_left=True, margin=0, dy=0, dh=0):

    x = 0 if from_left else -width
    dx = margin if from_left else -margin
    return _geometry_dict(x=x, w=width, dx=dx, dy=dy, dh=dh)


# ----------------------------------------------------------------------------
