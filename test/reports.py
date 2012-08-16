# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase

from hamcrest import assert_that, is_, is_not, contains_string, greater_than
from nose.tools import nottest

import doublex
from doublex.internal import InvocationSet, Invocation, InvocationContext


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


class SpyReportTest(TestCase):
    def assert_with_message(self, value, matcher, message):
        try:
            assert_that(value, matcher)
            self.fail("Exception should be raised")
        except AssertionError, e:
            print e
            assert_that(str(e), is_(message))

    def test_called_failed(self):
        spy = doublex.Spy()

        self.assert_with_message(
            spy.expected, doublex.called(),
            '''
Expected: this call:
          Spy.expected(ANY_ARG)
     but: calls that actually ocurred were:
          None\n''')

    def test_nerver_called_failed(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(5)

        self.assert_with_message(
            spy.unexpected, doublex.never(doublex.called()),
            '''
Expected: not this call:
          Spy.unexpected(ANY_ARG)
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)
          Spy.unexpected(5)\n''')

    def test_hamcrest_not_called_failed(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(5)

        self.assert_with_message(
            spy.unexpected, is_not(doublex.called()),
            '''
Expected: not this call:
          Spy.unexpected(ANY_ARG)
     but: was \n''')

    def test_called_with_failed(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)

        self.assert_with_message(
            spy.expected, doublex.called_with(3),
            '''
Expected: this call:
          Spy.expected(3)
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)\n''')

    def test_never_called_with_failed(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected, doublex.never(doublex.called_with(2)),
            '''
Expected: not this call:
          Spy.unexpected(2)
     but: calls that actually ocurred were:
          Spy.foo(1)
          Spy.foo(2)
          Spy.unexpected(2)\n''')

    def test_hamcrest_not_called_with_failed(self):
        spy = doublex.Spy()

        spy.foo(1)
        spy.foo(2)
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected, is_not(doublex.called_with(2)),
            '''
Expected: not this call:
          Spy.unexpected(2)
     but: was \n''')

    def test_called_with_matcher_failed(self):
        spy = doublex.Spy()

        self.assert_with_message(
            spy.unexpected,
            doublex.called_with(greater_than(1)),
            '''
Expected: this call:
          Spy.unexpected(a value greater than <1>)
     but: calls that actually ocurred were:
          None\n''')

    def test_never_called_with_matcher_failed(self):
        spy = doublex.Spy()
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected,
            doublex.never(doublex.called_with(greater_than(1))),
            '''
Expected: not this call:
          Spy.unexpected(a value greater than <1>)
     but: calls that actually ocurred were:
          Spy.unexpected(2)\n''')

    def test_hamcrest_not_called_with_matcher_failed(self):
        spy = doublex.Spy()
        spy.unexpected(2)

        self.assert_with_message(
            spy.unexpected,
            is_not(doublex.called_with(greater_than(1))),
            '''
Expected: not this call:
          Spy.unexpected(a value greater than <1>)
     but: was \n''')


class MockReportTest(TestCase):
    def setUp(self):
        self.mock = doublex.Mock()

    def assert_expectation_error(self, expected_message):
        try:
            assert_that(self.mock, doublex.meets_expectations())
            self.fail("This should raise exception")
        except AssertionError, e:
            assert_that(str(e), is_(expected_message))

    def test_expect_none_but_someting_unexpected_called(self):
        expected_message = '''
Expected: these calls:
          None
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
          None
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
          None
'''

        self.assert_expectation_error(expected_message)

    def test_expect_method_with_2_int_args_returning_int_but_nothing_called(self):
        with self.mock:
            self.mock.foo(1, 2).returns(1)

        expected_message = '''
Expected: these calls:
          Mock.foo(1, 2)-> 1
     but: calls that actually ocurred were:
          None
'''

        self.assert_expectation_error(expected_message)

    def test_except_method_with_2_str_args_returning_str_but_nothing_called(self):
        with self.mock:
            self.mock.foo('a', 'b').returns('c')

        expected_message = '''
Expected: these calls:
          Mock.foo('a', 'b')-> 'c'
     but: calls that actually ocurred were:
          None
'''

        self.assert_expectation_error(expected_message)

    def test_except_method_with_2_kwargs_returning_dict_but_nothing_called(self):
        with self.mock:
            self.mock.foo(num=1, color='red').returns({'key': 1})

        expected_message = '''
Expected: these calls:
          Mock.foo(color='red', num=1)-> {'key': 1}
     but: calls that actually ocurred were:
          None
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
