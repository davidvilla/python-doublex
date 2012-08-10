# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect
import exceptions

from hamcrest.core.base_matcher import BaseMatcher

import tools
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

    def assert_match_signature(self, invocation):
        pass

    def same_method(self, name1, name2):
        return name1 == name2


class Proxy(object):
    def __init__(self, collaborator):
        self.collaborator = collaborator
        self.collaborator_class = self.get_class(collaborator)

    def get_class(self, something):
        if inspect.isclass(something):
            return something
        else:
            return something.__class__

    def assert_match_signature(self, invocation):
        self.assert_has_method(invocation.name)
        method = getattr(self.collaborator, invocation.name)
        argspec = inspect.getargspec(method)

#        print method.__class__

#        print len(invocation.context.args), len(argspec.args)
#        print "args:", argspec.args
#        print "varargs:", argspec.varargs
#        print "keywords:", argspec.keywords
#        print "defaults:", argspec.defaults

        positionals = tools.inspect_count_positionals(argspec)
        keywords = tools.inspect_get_keywords(argspec)

#        print keywords

        if len(invocation.context.args) != positionals:
            reason = "Mismatching positional arguments:\n%s" %\
                self.add_class_prefix(invocation.name,
                                      inspect.formatargspec(*argspec))
            raise ApiMismatch(reason)

#        print invocation, argspec

    def assert_has_method(self, name):
        if not hasattr(self.collaborator, name):
            reason = "No such method: %s" % self.add_class_prefix(name)
            raise ApiMismatch(reason)

    def add_class_prefix(self, name, args=''):
        return "%s.%s%s" % (self.collaborator_class.__name__, name, args)

    def same_method(self, name1, name2):
        return getattr(self.collaborator, name1) == \
            getattr(self.collaborator, name2)

    def perform_invocation(self, invocation):
        method = getattr(self.collaborator, invocation.name)
        return method(*invocation.context.args,
                       **invocation.context.kargs)


class Method(object):
    def __init__(self, double, name):
        self.double = double
        self.name = name

    def __call__(self, *args, **kargs):
        invocation = Invocation(self.double, self.name,
                                InvocationContext(*args, **kargs))

        retval = self.double.invoke(invocation)

        if self.double.recording:
            return invocation

        return retval

    def was_called(self, context, times):
        invocation = Invocation(self.double, self.name, context)
        return invocation.was_called(times)

    def __repr__(self):
        indent = ' ' * 8
        invocations = self.double.get_invocations_to(self.name)
        if not invocations:
            return "method '%s' never invoked" % self.name

        retval = "invoked this way:\n"
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
            self.context == other.context

    def __repr__(self):
        return "%s%s" % (self.name, self.context)


class InvocationContext(object):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.output = None
        self.exception = None

    def any_arg(self):
        return ANY_ARG in self.args

    def __eq__(self, other):
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
        arg_values = []
        if self.args:
            arg_values.append(self._format_args(self.args))
        if self.kargs:
            arg_values.append(self._format_kargs(self.kargs))

        return "(%s) -> %s" % (str.join(', ', arg_values),
                               repr(self.output))

    @staticmethod
    def _format_args(args):
        str_args = []
        for arg in args:
            if isinstance(arg, unicode):
                arg = safeunicode.get_string(arg)

            if isinstance(arg, (int, str, dict)):
                str_args.append(repr(arg))
            else:
                str_args.append(str(arg))

        return str.join(', ', str_args)

    @staticmethod
    def _format_kargs(kargs):
        items = ['%s=%s' % (key, repr(val))
                 for key, val in sorted(kargs.items())]

        return str.join(', ', items)


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
