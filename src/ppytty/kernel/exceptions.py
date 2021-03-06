# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------


class TrapException(Exception):

    pass



class TrapDestroyed(TrapException):

    pass



class TrapDoesNotExist(TrapException):

    pass



class TrapArgCountWrong(TrapException):

    pass


# ----------------------------------------------------------------------------
