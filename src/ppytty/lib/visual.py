# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

"""
visual.py

Helper functions returning dicts with visual information for Widgets: geometry
and color.
"""


def _geometry(x=0, y=0, w=1.0, h=1.0, dx=0, dy=0, dw=0, dh=0):

    return dict(x=x, y=y, w=w, h=h, dx=dx, dy=dy, dw=dw, dh=dh)



def geometry_full():

    return _geometry()



def geometry_h_bar(height, from_top=True, margin=0, dx=0, dw=0):

    y = 0 if from_top else -height
    dy = margin if from_top else -margin
    return _geometry(y=y, h=height, dx=dx, dy=dy, dw=dw)



def geometry_v_bar(width, from_left=True, margin=0, dy=0, dh=0):

    x = 0 if from_left else -width
    dx = margin if from_left else -margin
    return _geometry(x=x, w=width, dx=dx, dy=dy, dh=dh)



def color(bg=None):

    # TODO: add fg once the kernel api supports it
    return dict(bg=bg)


# ----------------------------------------------------------------------------
