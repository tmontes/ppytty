# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

from ppytty.kernel import state




# Utility callables to validate kernel state.

def _is_none(object, attr_name):

    return getattr(object, attr_name) is None


def _is_emtpy_list(object, attr_name):

    attr = getattr(object, attr_name)
    is_list_like = hasattr(attr, 'append')
    return is_list_like and len(attr) == 0


def _is_empty_dict(object, attr_name):

    attr = getattr(object, attr_name)
    is_dict_like = hasattr(attr, 'keys') and hasattr(attr, 'values')
    return is_dict_like and len(attr) == 0


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
#   Values: 2-tuple with (is_clear_callable, change_its_value_callable)

STATE_OBJECTS = {
    'tasks': {
        'top_task': (_is_none, _change_scalar),
        'runnable': (_is_emtpy_list, _change_list),
        'terminated': (_is_emtpy_list, _change_list),
        'parent': (_is_empty_dict, _change_dict),
        'children': (_is_empty_dict, _change_dict),
        'waiting_on_child': (_is_emtpy_list, _change_list),
        'waiting_on_key': (_is_emtpy_list, _change_list),
        'waiting_on_key_hq': (_is_emtpy_list, _change_list),
        'waiting_on_time': (_is_emtpy_list, _change_list),
        'waiting_on_time_hq': (_is_emtpy_list, _change_list),
        'trap_calls': (_is_empty_dict, _change_dict),
        'trap_results': (_is_empty_dict, _change_dict),
        'windows': (_is_empty_dict, _change_dict),
    },
    'io_fds': {
        'input': (_is_emtpy_list, _change_list),
        'output': (_is_emtpy_list, _change_list),
        'user_in': (_is_none, _change_scalar),
        'user_out': (_is_none, _change_scalar),
    },
    'state': {
        'now': (_is_none, _change_scalar),
        'terminal': (_is_none, _change_scalar),
        'all_windows': (_is_emtpy_list, _change_list),
    }
}



def _assert_has_attrs(object_name, object, attr_names):

    try:
        for attr_name in attr_names:
            _ = getattr(object, attr_name)
    except AttributeError:
        raise AssertionError(f'{object_name!r} has no attribute {attr_name!r}')



def _assert_attrs_are_clean(object_name, object, attrs_dict):

    for attr_name, attr_test_callables in attrs_dict.items():
        attr_is_clean, _ = attr_test_callables
        if not attr_is_clean(object, attr_name):
            raise AssertionError(f'{object_name!r}.{attr_name!r} is not clean.')



def _change_all_attrs(name, object, attrs_dict):

    for attr_name, attr_test_callables in attrs_dict.items():
        _, change_attr = attr_test_callables
        change_attr(object, attr_name)



class TestRun(unittest.TestCase):


    def setUp(self):

        state.reset()


    def test_state_attrs_exist(self):

        for attr_name, attr_dict in STATE_OBJECTS.items():
            state_object = getattr(state, attr_name)
            with self.subTest(attr_name=attr_name):
                _assert_has_attrs(attr_name, state_object, attr_dict.keys())


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
