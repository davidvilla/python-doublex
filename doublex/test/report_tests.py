# -*- coding:utf-8; tab-width:4; mode:python -*-

# doublex
#
# Copyright © 2012 David Villa Alises
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from unittest import TestCase

from hamcrest import assert_that, is_, is_not, contains_string, greater_than
from nose.tools import nottest

import doublex
from doublex.internal import Invocation, InvocationContext
from unit_tests import ObjCollaborator


def create_invocation(name, args=None, kargs=None, output=None):
    stub = doublex.Stub()

    args = args or tuple()
    kargs = kargs or {}
    context = InvocationContext(*args, **kargs)
    context.output = output
    invocation = Invocation(stub, name, context)
    return invocation


class InvocationReportTests(TestCase):
    def test_int_arg_method_returning_int(self):
        invocation = create_invocation('foo', (1,), None, output=1)
        assert_that(str(invocation), is_('Stub.foo(1)-> 1'))

    def test_ANY_arg_method_returning_none(self):
        invocation = create_invocation('foo', (doublex.ANY_ARG,))
        assert_that(str(invocation), is_('Stub.foo(ANY_ARG)'))

#    @nottest
#    def test_unicode_arg_method(self):
#        self.add_invocation('foo', (u'ñandú',))
#
#        print self.render()
#
#        assert_that(self.render(),
#                    is_("foo(u'ñandú')"))


class MessageMixin(object):
    def assert_with_message(self, value, matcher, message):
        try:
            assert_that(value, matcher)
            self.fail("Exception should be raised")
        except AssertionError, e:
            assert_that(str(e).strip(), is_(message.strip()))


class SpyReportTest(TestCase, MessageMixin):
    def test_called(self):
        spy = doublex.Spy()

        expected = '''
Expected: these calls:
          Spy.expected(ANY_ARG)
     but: calls that actually ocurred were:
          No one'''

        self.assert_with_message(spy.expected, doublex.called(),
                                 expected)

    def test_nerver_called(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(5)

        self.assert_with_message(
            spy.unexpected, doublex.never(doublex.called()),
            '''
Expected: none of these calls:
          Spy.unexpected(ANY_ARG)
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)
          Spy.unexpected(5)''')

    def test_hamcrest_not_called(self):
        spy = doublex.Spy()
        spy.foo(1)
        spy.foo(2)
        spy.unexpected(5)

        self.assert_with_message(
            spy.unexpected, is_not(doublex.called()),
            '''
Expected: not these calls:
          Spy.unexpected(ANY_ARG)
     but: was ''')

    def test_called_times_int(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)

        self.assert_with_message(
            spy.foo, doublex.called().times(1),
            '''
Expected: these calls:
          Spy.foo(ANY_ARG) -- times: 1
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)''')

    def test_called_times_matcher(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)

        self.assert_with_message(
            spy.foo, doublex.called().times(greater_than(3)),
            '''
Expected: these calls:
          Spy.foo(ANY_ARG) -- times: a value greater than <3>
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)''')

    def test_called_with(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)

        self.assert_with_message(
            spy.expected, doublex.called().with_args(3),
            '''
Expected: these calls:
          Spy.expected(3)
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)''')

    def test_never_called_with(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected, doublex.never(doublex.called().with_args(2)),
            '''
Expected: none of these calls:
          Spy.unexpected(2)
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)
          Spy.unexpected(2)''')

    def test_hamcrest_not_called_with(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected, is_not(doublex.called().with_args(2)),
            '''
Expected: not these calls:
          Spy.unexpected(2)
     but: was ''')

    def test_called_with_matcher(self):
        spy = doublex.Spy()

        self.assert_with_message(
            spy.unexpected,
            doublex.called().with_args(greater_than(1)),
            '''
Expected: these calls:
          Spy.unexpected(a value greater than <1>)
     but: calls that actually ocurred were:
          No one''')

    def test_never_called_with_matcher(self):
        spy = doublex.Spy()
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected,
            doublex.never(doublex.called().with_args(greater_than(1))),
            '''
Expected: none of these calls:
          Spy.unexpected(a value greater than <1>)
     but: calls that actually ocurred were:
          Spy.unexpected(2)''')

    def test__hamcrest_not__called_with_matcher(self):
        spy = doublex.Spy()
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected,
            is_not(doublex.called().with_args(greater_than(1))),
            '''
Expected: not these calls:
          Spy.unexpected(a value greater than <1>)
     but: was ''')


class MockReportTest(TestCase, MessageMixin):
    def setUp(self):
        self.mock = doublex.Mock()

    def assert_expectation_error(self, expected_message):
        self.assert_with_message(self.mock, doublex.verify(),
                                 expected_message)

    def test_expect_none_but_someting_unexpected_called(self):
        expected_message = '''
Expected: these calls:
          No one
     but: this call was not expected:
          Mock.unexpected()
'''

        try:
            self.mock.unexpected()
            self.fail("This should raise exception")
        except AssertionError, e:
            assert_that(str(e), is_(expected_message))

    def test_expect_1_void_method_but_nothing_called(self):
        with self.mock:
            self.mock.expected()

        expected_message = '''
Expected: these calls:
          Mock.expected()
     but: calls that actually ocurred were:
          No one
'''

        self.assert_expectation_error(expected_message)

    def test_expect_2_void_methods_but_nothing_called(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        expected_message = '''
Expected: these calls:
          Mock.foo()
          Mock.bar()
     but: calls that actually ocurred were:
          No one
'''

        self.assert_expectation_error(expected_message)

    def test_expect_method_with_2_int_args_returning_int_but_nothing_called(self):
        with self.mock:
            self.mock.foo(1, 2).returns(1)

        expected_message = '''
Expected: these calls:
          Mock.foo(1, 2)-> 1
     but: calls that actually ocurred were:
          No one
'''

        self.assert_expectation_error(expected_message)

    def test_except_method_with_2_str_args_returning_str_but_nothing_called(self):
        with self.mock:
            self.mock.foo('a', 'b').returns('c')

        expected_message = '''
Expected: these calls:
          Mock.foo('a', 'b')-> 'c'
     but: calls that actually ocurred were:
          No one
'''

        self.assert_expectation_error(expected_message)

    def test_except_method_with_2_kwargs_returning_dict_but_nothing_called(self):
        with self.mock:
            self.mock.foo(num=1, color='red').returns({'key': 1})

        expected_message = '''
Expected: these calls:
          Mock.foo(color='red', num=1)-> {'key': 1}
     but: calls that actually ocurred were:
          No one
'''

        self.assert_expectation_error(expected_message)

    def test_expect_4_calls_but_only_2_called(self):
        with self.mock:
            self.mock.foo()
            self.mock.foo()
            self.mock.bar()
            self.mock.bar()

        self.mock.foo()
        self.mock.bar()

        expected_message = '''
Expected: these calls:
          Mock.foo()
          Mock.foo()
          Mock.bar()
          Mock.bar()
     but: calls that actually ocurred were:
          Mock.foo()
          Mock.bar()
'''

        self.assert_expectation_error(expected_message)


class PropertReportTests(TestCase, MessageMixin):
    def test_expected_get(self):
        spy = doublex.Spy(ObjCollaborator)

        expected_message = '''
Expected: these calls:
          get ObjCollaborator.prop
     but: calls that actually ocurred were:
          No one
'''

        self.assert_with_message(
            spy, doublex.property_got('prop'),
            expected_message)

    def test_unexpected_get(self):
        expected_message = '''
Expected: none of these calls:
          get ObjCollaborator.prop
     but: calls that actually ocurred were:
          get ObjCollaborator.prop
'''

        spy = doublex.Spy(ObjCollaborator)
        spy.prop

        self.assert_with_message(
            spy, doublex.never(doublex.property_got('prop')),
            expected_message)

    def test_expected_set(self):
        spy = doublex.Spy(ObjCollaborator)

        expected_message = '''
Expected: these calls:
          set ObjCollaborator.prop to ANYTHING
     but: calls that actually ocurred were:
          No one
'''

        self.assert_with_message(
            spy, doublex.property_set('prop'),
            expected_message)

    def test_unexpected_set(self):
        expected_message = '''
Expected: none of these calls:
          set ObjCollaborator.prop to ANYTHING
     but: calls that actually ocurred were:
          set ObjCollaborator.prop to unexpected
'''

        spy = doublex.Spy(ObjCollaborator)
        spy.prop = 'unexpected'

        self.assert_with_message(
            spy, doublex.never(doublex.property_set('prop')),
            expected_message)
