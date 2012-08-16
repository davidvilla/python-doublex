# -*- coding:utf-8; tab-width:4; mode:python -*-

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher

from internal import Method, InvocationContext, ANY_ARG
from exc import WrongApiUsage


class MethodCalled(BaseMatcher):
    def __init__(self, context, times=None):
        self.context = context
        self._times = times or hamcrest.greater_than(0)

    def _matches(self, method):
        self.method = method
        if not isinstance(method, Method):
            raise WrongApiUsage(
                "item must be a double method, not %s" % method)

        return method.was_called(self.context, self._times)

    def describe_to(self, description):
        description.append_text('this call:\n')
        description.append_text(self.method.show(indent=10))
        description.append_text(str(self.context))
#        description.append_text(' ')
#        if self._times > 1:
#            description.append_text('%s times ' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text("calls that actually ocurred were:\n")
        description.append_text(self.method.double.invocations.show(indent=10))

    def times(self, n):
        return MethodCalled(self.context, times=n)


def called():
    return MethodCalled(InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return MethodCalled(InvocationContext(*args, **kargs))


class never(BaseMatcher):
    def __init__(self, matcher):
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
        return self.invocation in mock.stubs

    def describe_to(self, description):
        description.append_text("these calls:\n")
        description.append_text(self.mock.stubs.show(indent=10))

    def describe_mismatch(self, actual, description):
        description.append_text("this call was not expected:\n")
        description.append_text(self.invocation.show(indent=10))


class MockMeetsExpectations(BaseMatcher):
    def _matches(self, mock):
        self.mock = mock
        return mock.stubs == mock.invocations

    def describe_to(self, description):
        description.append_text("these calls:\n")
        description.append_text(self.mock.stubs.show(indent=10))

    def describe_mismatch(self, actual, description):
        description.append_text('calls that actually ocurred were:\n')
        description.append_text(self.mock.invocations.show(indent=10))


def meets_expectations():
    return MockMeetsExpectations()


# just aliases
at_least = hamcrest.greater_than_or_equal_to
at_most = hamcrest.less_than_or_equal_to
