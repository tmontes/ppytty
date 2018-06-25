# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from .. import tasks



class Slide(tasks.Parallel):

    def run(self):

        yield ('direct-clear',)
        result = yield from super().run()
        return result


# ----------------------------------------------------------------------------
