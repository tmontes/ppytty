# ----------------------------------------------------------------------------
# ppytty
# ----------------------------------------------------------------------------
# Copyright (c) Tiago Montes.
# See LICENSE for deatils.
# ----------------------------------------------------------------------------

import unittest

from ppytty.kernel.state import state

from . import helper_state



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

        _assert_attrs_are_these('state', state, helper_state.STATE_ATTRS.keys())


    def test_state_attrs_are_clean(self):

        _assert_attrs_are_clean('state', state, helper_state.STATE_ATTRS)


    def test_state_reset(self):

        _change_all_attrs('state', state, helper_state.STATE_ATTRS)
        state.reset()
        _assert_attrs_are_clean('state', state, helper_state.STATE_ATTRS)


# ----------------------------------------------------------------------------
