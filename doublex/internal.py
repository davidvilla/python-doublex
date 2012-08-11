# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect
import exceptions

from hamcrest.core.base_matcher import BaseMatcher

import safeunicode
from .exc import *
from .const import *


class InvocationSet(list):
    def lookup(self, invocation):
        if not invocation in self:
            raise LookupError

        i = self.index(invocation)
        return self[i]

    def __repr__(self):
        if not self:
            return "No one"

        return super(InvocationSet, self).__repr__()


def create_proxy(collaborator):
    if collaborator is None:
        return DummyProxy()

    return Proxy(collaborator)


class DummyProxy(object):
    def assert_has_method(self, name):
        pass

    def assert_signature_matches(self, invocation):
        pass

    def same_method(self, name1, name2):
        return name1 == name2

    def collaborator_classname(self):
        return None


class Proxy(object):
    def __init__(self, collaborator):
        self.collaborator = collaborator
        self.collaborator_class = self.get_class()

    def isclass(self):
        return inspect.isclass(self.collaborator)

    def get_class(self):
        if self.isclass():
            return self.collaborator
        else:
            return self.collaborator.__class__

    def collaborator_classname(self):
        return self.collaborator_class.__name__

    def assert_signature_matches(self, invocation):
        self.assert_has_method(invocation.name)
        signature = Signature(self, invocation.name)
        try:
            signature.assert_match(invocation.context.args,
                                   invocation.context.kargs)
        except TypeError, e:
            template = """
  reason:     %s
  invocation: %s
  signature:  %s
"""
            message = template % (str(e), invocation, signature)
            raise ApiMismatch(message)

    def assert_has_method(self, name):
        if not hasattr(self.collaborator, name):
            reason = "Not such method: %s.%s" % \
                (self.collaborator_classname(), name)
            raise ApiMismatch(reason)

    def same_method(self, name1, name2):
        return getattr(self.collaborator, name1) == \
            getattr(self.collaborator, name2)

    def perform_invocation(self, invocation):
        method = getattr(self.collaborator, invocation.name)
        return method(*invocation.context.args,
                       **invocation.context.kargs)


class Signature(object):
    """colaborator method signature"""
    def __init__(self, proxy, name):
        self.proxy = proxy
        self.name = name
        self.method = getattr(proxy.collaborator, name)
        self.argspec = inspect.getargspec(self.method)

#        print "signature:", self.method
#        print "class:    ", self.method.__class__
#        print "args(%s):   %s" % (len(self.argspec.args), self.argspec.args)
#        print "varargs:  ", self.argspec.varargs
#        print "keywords: ", self.argspec.keywords
#        print "defaults: ", self.argspec.defaults

#    def count_positionals(self):
#        if self.argspec.defaults is None:
#            ndefaults = 0
#        else:
#            ndefaults = len(self.argspec.defaults)
#
#        return len(self.argspec.args) - ndefaults - 1
#
#    def get_keywords(self):
#        if self.argspec.defaults is None:
#            return []
#
#        return self.argspec.args[-len(self.argspec.defaults):]

    def assert_match(self, args, kargs):
        if self.proxy.isclass():
            args = (None,) + args  # self

        # This requires python-2.7!!!
        inspect.getcallargs(self.method, *args, **kargs)

    def __repr__(self):
        return "%s.%s%s" % (self.proxy.collaborator_classname(),
                            self.name,
                            inspect.formatargspec(*self.argspec))


class Method(object):
    def __init__(self, double, name):
        self.double = double
        self.name = name

    def __call__(self, *args, **kargs):
        invocation = self.get_invocation(args, kargs)
        retval = self.double.invoke(invocation)

        if self.double.recording:
            return invocation

        return retval

    def get_invocation(self, args, kargs):
        return Invocation(self.double, self.name,
                          InvocationContext(*args, **kargs))

    def was_called(self, context, times):
        invocation = Invocation(self.double, self.name, context)
        return invocation.was_called(times)

    def __repr__(self):
        indent = ' ' * 8
        method = "method '%s.%s'" % (self.double.classname(), self.name)
        invocations = self.double.get_invocations_to(self.name)
        if not invocations:
            return method + " never invoked"

        retval = method + " was invoked this way:\n"
        for i in invocations:
            retval += "%s%s\n" % (indent, i)

        return retval


class Invocation(object):
    def __init__(self, double, name, context):
        self.double = double
        self.name = name
        self.context = context

    def was_called(self, times):
        return self.double.was_called(self, times)

    def returns(self, value):
        self.context.output = value
        return self

    def returns_input(self):
        if not self.context.args:
            raise ApiMismatch

        self.returns(self.context.args)
        return self

    def raises(self, value):
        self.context.exception = value

    def times(self, n):
        if n < 2:
            raise WrongApiUsage()

        for i in range(1, n):
            self.double.invoke(self)

    def __eq__(self, other):
        return self.double.proxy.same_method(self.name, other.name) and \
            self.context.matches(other.context)

    def __repr__(self):
        return "%s.%s%s" % (self.double.classname(), self.name, self.context)


class InvocationContext(object):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.output = None
        self.exception = None

    def any_arg(self):
        return ANY_ARG in self.args

    def matches(self, other):
        if self.any_arg() or other.any_arg():
            return True

        return (self.args, self.kargs) == (other.args, other.kargs)

    def __str__(self):
        return str(InvocationFormatter(self))


class InvocationFormatter(object):
    def __init__(self, context):
        self.args = context.args
        self.kargs = context.kargs
        self.output = context.output

    def __str__(self):
        arg_values = self._format_args(self.args)
        arg_values.extend(self._format_kargs(self.kargs))

        retval = "(%s)" % str.join(', ', arg_values)
        if self.output is not None:
            retval += "-> %s" % repr(self.output)
        return retval

    @staticmethod
    def _format_args(args):
        items = []
        for arg in args:
            if isinstance(arg, unicode):
                arg = safeunicode.get_string(arg)

            if isinstance(arg, (int, str, dict)):
                items.append(repr(arg))
            else:
                items.append(str(arg))

        return items

    @staticmethod
    def _format_kargs(kargs):
        return ['%s=%s' % (key, repr(val))
                for key, val in sorted(kargs.items())]


class MethodCalled(BaseMatcher):
    def __init__(self, context, times=1):
        self.context = context
        self._times = times

    def _matches(self, method):
        if not isinstance(method, Method):
            raise WrongApiUsage()

        return method.was_called(self.context, self._times)

    def describe_to(self, description):
        description.append_text('method called with ')
        description.append_text(str(self.context))
        description.append_text(' ')
        if self._times > 1:
            description.append_text('%s times ' % self._times)

    def times(self, n):
        return MethodCalled(self.context, times=n)


class MockMeetsExpectations(BaseMatcher):
    def _matches(self, mock):
#        if not instance(mock, Mock):
#            raise WrongApiUsage()

#        print mock.stubs
#        print mock.invocations
#        print mock.stubs == mock.invocations
        return mock.stubs == mock.invocations

    def describe_to(self, description):
        description.append_text('invocations ')
