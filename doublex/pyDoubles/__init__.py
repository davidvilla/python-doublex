# -*- coding:utf-8; tab-width:4; mode:python -*-

"""
This is a wrapper to offer the pyDoubles API but implemented
over doublex package.
"""

import hamcrest
from hamcrest.library.object.hasproperty import has_property

import doublex

from doublex import ANY_ARG, method_returning, method_raising, WrongApiUsage

UnexpectedBehavior = AssertionError
ArgsDontMatch = AssertionError
ApiMismatch = TypeError


def empty_spy():
    return doublex.Spy()


def spy(collaborator=None):
    return doublex.Spy(collaborator)


def proxy_spy(collaborator):
    return doublex.ProxySpy(collaborator)


def empty_mock():
    return mock()


def assert_that_was_called(method):
    return assert_that_method(method).was_called()


class mock(doublex.Mock):
    def assert_that_is_satisfied(self):
        hamcrest.assert_that(self, doublex.verify())

    def assert_expectations(self):
        self.assert_that_is_satisfied()


class expect_call(object):
    def __init__(self, method):
        if not isinstance(method, doublex.internal.Method):
            raise doublex.WrongApiUsage

        self.method = method
        self.invocation = None
        self.with_args(ANY_ARG)

    def with_args(self, *args, **kargs):
        self.args = args
        self.kargs = kargs

        self._remove_previous()
        with self.method.double:
            self.invocation = self.method(*args, **kargs)
        return self

    def returning(self, value):
        self._remove_previous()
        with self.method.double:
            self.invocation = self.method(*self.args, **self.kargs).returns(value)
        return self

    def times(self, n):
        if n < 2:
            raise doublex.WrongApiUsage

        with self.method.double:
            for i in range(n - 1):
                self.method.double._manage_invocation(self.invocation)

    def _remove_previous(self):
        if self.invocation is None:
            return

        self.method.double._stubs.remove(self.invocation)


class when(object):
    def __init__(self, method):
        self.method = method
        self.args = (ANY_ARG, )
        self.kargs = {}

    def with_args(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        return self

    def then_return(self, output):
        with self.method.double:
            self.method(*self.args, **self.kargs).returns(output)

    def then_return_input(self):
        with self.method.double:
            self.method(*self.args, **self.kargs).returns_input()

    def then_raise(self, e):
        with self.method.double:
            self.method(*self.args, **self.kargs).raises(e)


class assert_that_method(object):
    def __init__(self, method):
        if not isinstance(method, doublex.internal.Method):
            raise doublex.WrongApiUsage()

        self.method = method
        self.args = (ANY_ARG,)
        self.kargs = {}

    def was_called(self):
        return self.with_args(*self.args, **self.kargs)

    def was_never_called(self):
        hamcrest.assert_that(self.method,
                             doublex.matchers.never(doublex.called()))

    def with_args(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        hamcrest.assert_that(self.method,
                             doublex.called().with_args(*args, **kargs))
        return self

    def times(self, n):
        hamcrest.assert_that(
            self.method,
            doublex.called().with_args(*self.args, **self.kargs).times(
                hamcrest.greater_than_or_equal_to(n)))


#-- pyDoubles matchers --

str_containing = hamcrest.contains_string
str_not_containing = lambda x: hamcrest.is_not(hamcrest.contains_string(x))
str_length = hamcrest.has_length


def obj_with_fields(fields):
    if not isinstance(fields, dict):
        raise doublex.WrongApiUsage

    matchers = []
    for key, value in list(fields.items()):
        matchers.append(has_property(key, value))

    return hamcrest.all_of(*matchers)
