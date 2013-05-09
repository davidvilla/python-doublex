# -*- coding: utf-8 -*-

"""
Authors:
    Carlos Ble (www.carlosble.com)
    Ruben Bernardez (www.rubenbp.com)
    www.iExpertos.com
License: Apache 2 (http://www.apache.org/licenses/LICENSE-2.0.html)
Project home: https://bitbucket.org/carlosble/pydoubles
"""

import unittest
from hamcrest.core.core import *
from hamcrest.library.collection.isdict_containing import has_entry
from hamcrest.library.object.haslength import has_length
from hamcrest.library.text.isequal_ignoring_case import equal_to_ignoring_case
from hamcrest.library.text.stringstartswith import starts_with
from doublex.pyDoubles import *
from unit_tests import Collaborator


class HamcrestIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.spy = spy(Collaborator())

    def test_use_in_stub_method(self):
        when(self.spy.one_arg_method).with_args(
                    starts_with('tt')).then_return(1000)
        self.assertEquals(1000, self.spy.one_arg_method('ttxe'))

    def test_use_in_spy_call(self):
        self.spy.one_arg_method('ttxe')
        assert_that_was_called(
            self.spy.one_arg_method).with_args(starts_with('tt'))

    def test_is_matcher(self):
        class Customer:
            pass
        customer = Customer()
        when(self.spy.one_arg_method).with_args(
            is_(customer)).then_return(1000)
        self.assertEquals(1000, self.spy.one_arg_method(customer))

    def test_instance_of_matcher(self):
        when(self.spy.one_arg_method).with_args(
            instance_of(int)).then_return(1000)
        self.assertEquals(1000, self.spy.one_arg_method(5))

    def test_all_of_matcher(self):
        text = 'hello'
        when(self.spy.one_arg_method).with_args(
            all_of(starts_with('h'), equal_to(text))).then_return(1000)
        self.assertEquals(1000, self.spy.one_arg_method(text))

    def test_has_length_matcher(self):
        list = [10, 20, 30]
        when(self.spy.one_arg_method).with_args(
            has_length(3)).then_return(1000)
        self.assertEquals(1000, self.spy.one_arg_method(list))

    def test_has_entry_matcher(self):
        list = {'one': 1, 'two': 2}
        when(self.spy.one_arg_method).with_args(
            has_entry(equal_to('two'), 2)).then_return(1000)
        self.assertEquals(1000, self.spy.one_arg_method(list))

    def test_equal_to_ignoring_case_matcher(self):
        self.spy.one_arg_method('hello')
        assert_that_was_called(self.spy.one_arg_method).with_args(
            equal_to_ignoring_case('HEllO'))

    def test_matcher_error_is_human_readable(self):
        self.spy.one_arg_method('xe')
        try:
            assert_that_method(self.spy.one_arg_method).was_called().with_args(
                starts_with('tt'))
        except ArgsDontMatch, e:
            self.assertTrue("tt" in str(e.args))
            self.assertTrue("string starting" in str(e.args))


if __name__ == "__main__":
    print "Use nosetest to run this tests: nosetest hamcrest_integration.py"
