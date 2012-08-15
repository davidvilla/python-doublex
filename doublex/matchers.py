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
        if not isinstance(method, Method):
            raise WrongApiUsage(
                "item must be a double method, not %s" % method)

        return method.was_called(self.context, self._times)

    def describe_to(self, description):
        description.append_text('called with ')
        description.append_text(str(self.context))
        description.append_text(' ')
        if self._times > 1:
            description.append_text('%s times ' % self._times)

    def times(self, n):
        return MethodCalled(self.context, times=n)


def called():
    return MethodCalled(InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return MethodCalled(InvocationContext(*args, **kargs))


class MockMeetsExpectations(BaseMatcher):
    def _matches(self, mock):
        return mock.stubs == mock.invocations

    def describe_to(self, description):
        description.append_text('invocations ')


def meets_expectations():
    return MockMeetsExpectations()


# just aliases
at_least = hamcrest.greater_than_or_equal_to
at_most = hamcrest.less_than_or_equal_to
