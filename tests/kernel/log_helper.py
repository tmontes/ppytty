# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

import logging



class Handler(logging.Handler):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.messages = []


    def emit(self, record):

        self.messages.append(self.format(record))



def create_and_add_handler(level=logging.WARNING):

    handler = Handler()

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    return handler



def remove_handler(h):

    root_logger = logging.getLogger()
    root_logger.removeHandler(h)


# ----------------------------------------------------------------------------
