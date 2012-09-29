# -*- coding:utf-8; tab-width:4; mode:python -*-

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import assert_that, is_

from internal import Method, InvocationContext, ANY_ARG, MockBase, SpyBase, PropertyGet, PropertySet
from internal import WrongApiUsage

__all__ = ['called',
           'never',
           'verify', 'any_order_verify',
           'property_got', 'property_set',
           'assert_that', 'is_']


any_time = hamcrest.greater_than(0)


class OperationMatcher(BaseMatcher):
    pass


class MethodCalled(OperationMatcher):
    def __init__(self, context=None, times=any_time):
        self.context = context or InvocationContext(ANY_ARG)
        self._times = times

    def _matches(self, method):
        self._assure_is_spied_method(method)
        self.method = method
        return method._was_called(self.context, self._times)

    def _assure_is_spied_method(self, method):
        if not isinstance(method, Method) or not isinstance(method.double, SpyBase):
            raise WrongApiUsage("takes a spy method (got %s instead)" % method)

    def describe_to(self, description):
        description.append_text('these calls:\n')
        description.append_text(self.method.show(indent=10))
        description.append_text(str(self.context))
        if self._times != any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text("calls that actually ocurred were:\n")
        description.append_text(self.method.double._recorded.show(indent=10))

    def with_args(self, *args, **kargs):
        self.context.update_args(args, kargs)
        return self

    def times(self, n):
        self._times = n
        return self


def called():
    return MethodCalled()


class never(BaseMatcher):
    def __init__(self, matcher):
        if not isinstance(matcher, OperationMatcher):
            raise WrongApiUsage(
                "takes called/called_with instance (got %s instead)" % matcher)
        self.matcher = matcher

    def _matches(self, item):
        return not self.matcher.matches(item)

    def describe_to(self, description):
        description.append_text('none of ').append_description_of(self.matcher)

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


# FIXME: refactor describe mismatch
class property_got(OperationMatcher):
    def __init__(self, propname, times=any_time):
        super(property_got, self).__init__()
        self.propname = propname
        self._times = times

    def _matches(self, double):
        self.double = double
        self.operation = PropertyGet(self.double, self.propname)
        return double._was_called(self.operation, 1)

    def times(self, n):
        return property_got(self.property_name, n)

    def describe_to(self, description):
        description.append_text('these calls:\n')
        description.append_text(self.operation.show(indent=10))
#        description.append_text(str(self.value))
        if self._times != any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text('calls that actually ocurred were:\n')
        description.append_text(self.double._recorded.show(indent=10))


# FIXME: refactor describe mismatch
class property_set(OperationMatcher):
    def __init__(self, property_name, value=hamcrest.anything(), times=any_time):
        super(property_set, self).__init__()
        self.property_name = property_name
        self.value = value
        self._times = times

    def _matches(self, double):
        self.double = double
        self.operation = PropertySet(self.double, self.property_name,
                                     self.value)
        return self.double._was_called(self.operation, self._times)

    def to(self, value):
        return property_set(self.property_name, value)

    def times(self, n):
        return property_set(self.property_name, self.value, n)

    def describe_to(self, description):
        description.append_text('these calls:\n')
        description.append_text(self.operation.show(indent=10))
        if self._times != any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text('calls that actually ocurred were:\n')
        description.append_text(self.double._recorded.show(indent=10))


# just aliases
at_least = hamcrest.greater_than_or_equal_to
at_most = hamcrest.less_than_or_equal_to
