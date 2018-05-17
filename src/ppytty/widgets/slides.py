# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from . import utils


class Slide(utils.Parallel):

    def run(self):

        yield ('clear',)
        result = yield from super().run()
        return result



class SlideDeck(utils.Serial):

    pass


# ----------------------------------------------------------------------------