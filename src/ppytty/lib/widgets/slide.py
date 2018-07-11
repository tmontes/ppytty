# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------


from .. import tasks



class Slide(tasks.Parallel):

    async def run(self):

        await self.api.direct_clear()
        result = await super().run()
        return result


# ----------------------------------------------------------------------------
