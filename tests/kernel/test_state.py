# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

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


# Utility callables to change kernel state.

def _change_scalar(object, attr_name):

    setattr(object, attr_name, 42)


def _change_list(object, attr_name):

    attr = getattr(object, attr_name)
    attr.append(42)


def _change_dict(object, attr_name):

    attr = getattr(object, attr_name)
    attr[42] = 42



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
    'tasks_waiting_key_hq': (_assert_empty_list, _change_list),
    'tasks_waiting_time': (_assert_empty_list, _change_list),
    'tasks_waiting_time_hq': (_assert_empty_list, _change_list),
    'trap_call': (_assert_empty_dict, _change_dict),
    'trap_success': (_assert_empty_dict, _change_dict),
    'trap_result': (_assert_empty_dict, _change_dict),
    'task_inbox': (_assert_empty_dict, _change_dict),
    'task_windows': (_assert_empty_dict, _change_dict),
    'all_windows': (_assert_empty_list, _change_list),
    'in_fds': (_assert_empty_list, _change_list),
    'out_fds': (_assert_empty_list, _change_list),
    'user_in_fd': (_assert_is_none, _change_scalar),
    'user_out_fd': (_assert_is_none, _change_scalar),
    'now': (_assert_is_none, _change_scalar),
    'terminal': (_assert_is_none, _change_scalar),
}



def _assert_attrs_are_these(object_name, object, attr_names):

    # `object` has all attributes in `attr_names`
    try:
        for attr_name in attr_names:
            _ = getattr(object, attr_name)
    except AttributeError:
        raise AssertionError(f'{object_name!r} has no attribute {attr_name!r}')

    # no `object` attributes other than those in `attr_names`
    for attr_name in dir(object):
        if attr_name.startswith('_'):
            continue
        if callable(getattr(object, attr_name)):
            continue
        if attr_name not in attr_names:
            raise AssertionError(f'{object_name!r} untested attribute {attr_name!r}')



def _assert_attrs_are_clean(object_name, object, attrs_dict):

    for attr_name, attr_test_callables in attrs_dict.items():
        assert_attr_is_clean, _ = attr_test_callables
        try:
            assert_attr_is_clean(object, attr_name)
        except AssertionError as e:
            e.args = [f'{object_name!r}.{e.args[0]}']
            raise



def _change_all_attrs(name, object, attrs_dict):

    for attr_name, attr_test_callables in attrs_dict.items():
        _, change_attr = attr_test_callables
        change_attr(object, attr_name)



class TestRun(unittest.TestCase):


    def setUp(self):

        state.reset()


    def test_state_attrs_are_these(self):

        _assert_attrs_are_these('state', state, STATE_ATTRS.keys())


    def test_state_attrs_are_clean(self):

        _assert_attrs_are_clean('state', state, STATE_ATTRS)


    def test_state_reset(self):

        _change_all_attrs('state', state, STATE_ATTRS)
        state.reset()
        _assert_attrs_are_clean('state', state, STATE_ATTRS)


# ----------------------------------------------------------------------------
