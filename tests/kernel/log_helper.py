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
        self._ppytty_records = []


    def emit(self, record):

        self._ppytty_records.append(record)



def setup_handler(level):

    handler = Handler()

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    return handler


# ----------------------------------------------------------------------------