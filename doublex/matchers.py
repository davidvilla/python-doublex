# -*- coding:utf-8; tab-width:4; mode:python -*-

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import assert_that, is_

from internal import Method, InvocationContext, ANY_ARG, MockBase
from exc import WrongApiUsage

__all__ = ['called', 'called_with',
           'never',
           'verify', 'any_order_verify',
           'assert_that', 'is_']


class MethodCalled(BaseMatcher):
    any_time = hamcrest.greater_than(0)

    def __init__(self, context, times=None):
        self.context = context
        self._times = times or self.any_time

    def _matches(self, method):
        self.method = method
        if not isinstance(method, Method):
            raise WrongApiUsage(
                "takes a double method (got %s instead)" % method)

        return method._was_called(self.context, self._times)

    def describe_to(self, description):
        description.append_text('this call:\n')
        description.append_text(self.method.show(indent=10))
        description.append_text(str(self.context))
        if self._times != self.any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text("calls that actually ocurred were:\n")
        description.append_text(self.method.double._recorded.show(indent=10))

    def times(self, n):
        return MethodCalled(self.context, times=n)


def called():
    return MethodCalled(InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return MethodCalled(InvocationContext(*args, **kargs))


class never(BaseMatcher):
    def __init__(self, matcher):
        if not isinstance(matcher, MethodCalled):
            raise WrongApiUsage(
                "takes called/called_with instance (got %s instead)" % matcher)
        self.matcher = matcher

    def _matches(self, item):
        return not self.matcher.matches(item)

    def describe_to(self, description):
        description.append_text('not ').append_description_of(self.matcher)

    def describe_mismatch(self, actual, description):
        self.matcher.describe_mismatch(actual, description)


class MockExpectInvocation(BaseMatcher):
    def __init__(self, invocation):
        self.invocation = invocation

    def _matches(self, mock):
        self.mock = mock
        return self.invocation in mock._stubs

    def describe_to(self, description):
        description.append_text("these calls:\n")
        description.append_text(self.mock._stubs.show(indent=10))

    def describe_mismatch(self, actual, description):
        description.append_text("this call was not expected:\n")
        description.append_text(self.invocation.show(indent=10))


class verify(BaseMatcher):
    def _matches(self, mock):
        if not isinstance(mock, MockBase):
            raise WrongApiUsage(
                "takes Mock instance (got %s instead)" % mock)

        self.mock = mock
        return self._expectations_match()

    def _expectations_match(self):
        return self.mock._stubs == self.mock._recorded

    def describe_to(self, description):
        description.append_text("these calls:\n")
        description.append_text(self.mock._stubs.show(indent=10))

    def describe_mismatch(self, actual, description):
        description.append_text('calls that actually ocurred were:\n')
        description.append_text(self.mock._recorded.show(indent=10))


class any_order_verify(verify):
    def _expectations_match(self):
        return sorted(self.mock._stubs) == sorted(self.mock._recorded)


# just aliases
at_least = hamcrest.greater_than_or_equal_to
at_most = hamcrest.less_than_or_equal_to
