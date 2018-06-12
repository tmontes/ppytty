# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from . state import tasks



def clear_tasks_children(task):

    if not tasks.children[task]:
        del tasks.children[task]



def clear_tasks_requests_responses(task):

    for target in (tasks.requests, tasks.responses):
        if task in target:
            del target[task]


def clear_tasks_waiting_on_time_hq():

    if not tasks.waiting_on_time:
        tasks.waiting_on_time_hq.clear()


# TODO: Do we need a "clear_tasks_waiting_on_key_hq"? Probably.


# ----------------------------------------------------------------------------
