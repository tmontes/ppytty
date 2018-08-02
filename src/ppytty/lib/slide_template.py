# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------



class SlideTemplate(object):

    def __init__(self, widgets=None):

        self.widgets = widgets if widgets else ()


    def geometry(self, widget_index, widget_count):

        return None


# ----------------------------------------------------------------------------
