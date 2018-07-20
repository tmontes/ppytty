# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for details.
# ----------------------------------------------------------------------------

from ppytty.kernel.state import state



# Utility callables to validate kernel state.

def _assert_is_none(object, attr_name):

    value = getattr(object, attr_name)
    if value is not None:
        raise AssertionError(f'{attr_name!r} is not None: {value!r}')


def _assert_empty_list(object, attr_name):

    value = getattr(object, attr_name)
    if not hasattr(value, 'append'):
        raise AssertionError(f'{attr_name!r} not list-like: no append method')
    if len(value):
        raise AssertionError(f'{attr_name!r} with non-zero length: {value!r}')


def _assert_empty_dict(object, attr_name):

    value = getattr(object, attr_name)
    for expected_attr in ('keys', 'values', 'items'):
        if not hasattr(value, expected_attr):
            raise AssertionError(f'{attr_name!r} not dict-like: no {expected_attr} method')
    if len(value):
        raise AssertionError(f'{attr_name!r} with non-zero length: {value!r}')


def _assert_none_mapping_dict(object, attr_name):

    value = getattr(object, attr_name)
    for expected_attr in ('keys', 'values', 'items'):
        if not hasattr(value, expected_attr):
            raise AssertionError(f'{attr_name!r} not dict-like: no {expected_attr} method')
    if len(value) != 1:
        raise AssertionError(f'{attr_name!r} with non-1 length: {value!r}')
    expect_none = value[None]
    if expect_none is not None:
        raise AssertionError(f'None not mapped to None')


def _assert_empty_set(object, attr_name):

    value = getattr(object, attr_name)
    for expected_attr in ('add', 'remove', 'update'):
        if not hasattr(value, expected_attr):
            raise AssertionError(f'{attr_name!r} not set-like: no {expected_attr} method')
    if len(value):
        raise AssertionError(f'{attr_name!r} with non-zero length: {value!r}')


# Utility callables to change kernel state.

def _change_scalar(object, attr_name):

    setattr(object, attr_name, 42)


def _change_list(object, attr_name):

    attr = getattr(object, attr_name)
    attr.append(42)


def _change_dict(object, attr_name):

    attr = getattr(object, attr_name)
    attr[42] = 42


def _change_set(object, attr_name):

    attr = getattr(object, attr_name)
    attr.add(42)



# Keys: state module attribute name
# Values: dicts
#   Keys: object attribute name
#   Values: 2-tuple with (is_clear_assertion, change_its_value_callable)

STATE_ATTRS = {
    'top_task': (_assert_is_none, _change_scalar),
    'top_task_success': (_assert_is_none, _change_scalar),
    'top_task_result': (_assert_is_none, _change_scalar),
    'runnable_tasks': (_assert_empty_list, _change_list),
    'completed_tasks': (_assert_empty_dict, _change_dict),
    'parent_task': (_assert_empty_dict, _change_dict),
    'child_tasks': (_assert_empty_dict, _change_dict),
    'tasks_waiting_child': (_assert_empty_list, _change_list),
    'tasks_waiting_inbox': (_assert_empty_list, _change_list),
    'tasks_waiting_key': (_assert_empty_list, _change_list),
    'tasks_waiting_time': (_assert_empty_list, _change_list),
    'tasks_waiting_time_hq': (_assert_empty_list, _change_list),
    'tasks_waiting_processes': (_assert_empty_set, _change_set),
    'user_space_tasks': (_assert_empty_dict, _change_dict),
    'kernel_space_tasks': (_assert_empty_dict, _change_dict),
    'trap_call': (_assert_empty_dict, _change_dict),
    'trap_success': (_assert_empty_dict, _change_dict),
    'trap_result': (_assert_empty_dict, _change_dict),
    'task_inbox': (_assert_empty_dict, _change_dict),
    'task_windows': (_assert_empty_dict, _change_dict),
    'all_windows': (_assert_empty_list, _change_list),
    'focusable_windows': (_assert_empty_list, _change_list),
    'focused_window': (_assert_is_none, _change_scalar),
    'process_window': (_assert_empty_dict, _change_dict),
    'window_process': (_assert_none_mapping_dict, _change_dict),
    'task_processes': (_assert_empty_dict, _change_dict),
    'process_task': (_assert_empty_dict, _change_dict),
    'all_processes': (_assert_empty_dict, _change_dict),
    'completed_processes': (_assert_empty_dict, _change_dict),
    'in_fds': (_assert_empty_dict, _change_dict),
    'out_fds': (_assert_empty_list, _change_list),
    'close_fd_callables': (_assert_empty_list, _change_list),
    'close_when_done_fds': (_assert_empty_list, _change_list),
    'now': (_assert_is_none, _change_scalar),
    'terminal': (_assert_is_none, _change_scalar),
}



class StateAssertionsMixin(object):

    _TASK_CONTAINER_NAMES = (
        'runnable_tasks',
        'completed_tasks',
        'tasks_waiting_child',
        'tasks_waiting_inbox',
        'tasks_waiting_key',
        'tasks_waiting_time',
        'tasks_waiting_processes',
    )
    def assert_no_tasks(self):

        for task_container_name in StateAssertionsMixin._TASK_CONTAINER_NAMES:
            value = getattr(state, task_container_name)
            self.assertFalse(value, f'{task_container_name} not empty')


# ----------------------------------------------------------------------------