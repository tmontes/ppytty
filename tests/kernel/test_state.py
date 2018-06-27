# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

from ppytty.kernel import state




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

STATE_OBJECTS = {
    'tasks': {
        'top_task': (_assert_is_none, _change_scalar),
        'top_task_success': (_assert_is_none, _change_scalar),
        'top_task_result': (_assert_is_none, _change_scalar),
        'runnable': (_assert_empty_list, _change_list),
        'terminated': (_assert_empty_list, _change_list),
        'parent': (_assert_empty_dict, _change_dict),
        'children': (_assert_empty_dict, _change_dict),
        'waiting_child': (_assert_empty_list, _change_list),
        'waiting_key': (_assert_empty_list, _change_list),
        'waiting_key_hq': (_assert_empty_list, _change_list),
        'waiting_time': (_assert_empty_list, _change_list),
        'waiting_time_hq': (_assert_empty_list, _change_list),
        'trap_calls': (_assert_empty_dict, _change_dict),
        'trap_results': (_assert_empty_dict, _change_dict),
        'windows': (_assert_empty_dict, _change_dict),
    },
    'io_fds': {
        'input': (_assert_empty_list, _change_list),
        'output': (_assert_empty_list, _change_list),
        'user_in': (_assert_is_none, _change_scalar),
        'user_out': (_assert_is_none, _change_scalar),
    },
    'state': {
        'now': (_assert_is_none, _change_scalar),
        'terminal': (_assert_is_none, _change_scalar),
        'all_windows': (_assert_empty_list, _change_list),
    }
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

        for attr_name, attr_dict in STATE_OBJECTS.items():
            state_object = getattr(state, attr_name)
            with self.subTest(attr_name=attr_name):
                _assert_attrs_are_these(attr_name, state_object, attr_dict.keys())


    def test_state_attrs_are_clean(self):

        for attr_name, attr_dict in STATE_OBJECTS.items():
            state_object = getattr(state, attr_name)
            with self.subTest(attr_name=attr_name):
                _assert_attrs_are_clean(attr_name, state_object, attr_dict)


    def test_state_reset(self):

        for attr_name, attr_dict in STATE_OBJECTS.items():
            state_object = getattr(state, attr_name)
            with self.subTest(attr_name=attr_name):
                _change_all_attrs(attr_name, state_object, attr_dict)
                state.reset()
                _assert_attrs_are_clean(attr_name, state_object, attr_dict)


# ----------------------------------------------------------------------------
