# -*- coding:utf-8; tab-width:4; mode:python -*-

# doublex
#
# Copyright © 2012,2013 David Villa Alises
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

import sys
import time
import hamcrest
from hamcrest.core.matcher import Matcher
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import is_, instance_of

from .internal import (
    Method, InvocationContext, ANY_ARG, MockBase, SpyBase,
    PropertyGet, PropertySet, WrongApiUsage, Invocation)

__all__ = ['called',
           'never',
           'verify', 'any_order_verify',
           'property_got', 'property_set',
           'assert_that', 'wait_that',
           'is_', 'instance_of']


# just hamcrest aliases
at_least = hamcrest.greater_than_or_equal_to
at_most = hamcrest.less_than_or_equal_to
any_time = hamcrest.greater_than(0)


class MatcherRequiredError(Exception):
    pass


def assert_that(actual, matcher=None, reason=''):
    if matcher and not isinstance(matcher, Matcher):
        raise MatcherRequiredError("%s should be a hamcrest Matcher" % str(matcher))
    return hamcrest.assert_that(actual, matcher, reason)


def wait_that(actual, matcher, reason='', delta=1, timeout=5):
    '''
    Poll the given matcher each 'delta' seconds until 'matcher'
    matches 'actual' or 'timeout' is reached.
    '''
    exc = None
    init = time.time()
    timeout_reached = False
    while 1:
        try:
            if time.time() - init > timeout:
                timeout_reached = True
                break

            assert_that(actual, matcher, reason)
            break

        except AssertionError as e:
            time.sleep(delta)
            exc = e

    if timeout_reached:
        msg = exc.args[0] + ' after {0} seconds'.format(timeout)
        exc.args = msg,
        raise exc


class OperationMatcher(BaseMatcher):
    pass


class MethodCalled(OperationMatcher):
    def __init__(self, context=None, times=any_time):
        self.context = context or InvocationContext(ANY_ARG)
        self._times = times
        self._async_timeout = None

    def _matches(self, method):
        self._assure_is_spied_method(method)
        self.method = method
        if not self._async_timeout:
            return method._was_called(self.context, self._times)

        if self._async_timeout:
            if self._times != any_time:
                raise WrongApiUsage("'times' and 'async_mode' are exclusive")
            self.method._event.wait(self._async_timeout)

        return method._was_called(self.context, self._times)

    def _assure_is_spied_method(self, method):
        if not isinstance(method, Method) or not isinstance(method.double, SpyBase):
            raise WrongApiUsage("takes a spy method (got %s instead)" % method)

    def describe_to(self, description):
        description.append_text('these calls:\n')
        description.append_text(self.method._show(indent=10))
        description.append_text(str(self.context))
        if self._times != any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text("calls that actually ocurred were:\n")
        description.append_text(self.method.double._recorded.show(indent=10))

    def with_args(self, *args, **kargs):
        self.context.update_args(args, kargs)
        return self

    def with_some_args(self, **kargs):
        self.context.update_args(tuple(), kargs)
        self.context.check_some_args = True
        return self

    def async_mode(self, timeout):
        self._async_timeout = timeout
        return self

    def times(self, n):
        self._times = n
        return self


#  backward compatibility
if sys.version_info < (3, 7):
    setattr(MethodCalled, 'async', MethodCalled.async_mode)


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


class MockIsExpectedInvocation(BaseMatcher):
    'assert the invocation is a mock expectation'
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
        description.append_text(self.invocation._show(indent=10))


class verify(BaseMatcher):
    def _matches(self, mock):
        if not isinstance(mock, MockBase):
            raise WrongApiUsage("takes Mock instance (got %s instead)" % mock)

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


class property_got(OperationMatcher):
    def __init__(self, propname, times=any_time):
        super(property_got, self).__init__()
        self.propname = propname
        self._times = times

    def _matches(self, double):
        self.double = double
        self.operation = PropertyGet(self.double, self.propname)
        return double._received_invocation(
            self.operation, 1, cmp_pred=Invocation.__eq__)

    def times(self, n):
        self._times = n
        return self

    def describe_to(self, description):
        description.append_text('these calls:\n')
        description.append_text(self.operation._show(indent=10))
        if self._times != any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text('calls that actually ocurred were:\n')
        description.append_text(self.double._recorded.show(indent=10))


class property_set(OperationMatcher):
    def __init__(self, property_name, value=hamcrest.anything(), times=any_time):
        super(property_set, self).__init__()
        self.property_name = property_name
        self.value = value
        self._times = times

    def _matches(self, double):
        self.double = double
        self.operation = PropertySet(self.double, self.property_name, self.value)
        return self.double._received_invocation(
            self.operation, self._times, cmp_pred=Invocation.__eq__)

    def to(self, value):
        self.value = value
        return self

    def times(self, n):
        self._times = n
        return self

    def describe_to(self, description):
        description.append_text('these calls:\n')
        description.append_text(self.operation._show(indent=10))
        if self._times != any_time:
            description.append_text(' -- times: %s' % self._times)

    def describe_mismatch(self, actual, description):
        description.append_text('calls that actually ocurred were:\n')
        description.append_text(self.double._recorded.show(indent=10))
