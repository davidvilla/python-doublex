# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect
import itertools

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher

try:
    from functools import total_ordering
except ImportError:
    from py27_backports import total_ordering

try:
    from inspect import getcallargs
except ImportError:
    from py27_backports import getcallargs


import safeunicode
from .exc import *


class SingleValue:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


ANY_ARG = SingleValue('ANY_ARG')
IMPOSSIBLE = SingleValue('IMPOSSIBLE')


def add_indent(text, indent=0):
    return "%s%s" % (' ' * indent, text)


class InvocationList(list):
    def lookup(self, invocation):
        if not invocation in self:
            raise LookupError

        compatible = [i for i in self if i == invocation]
        compatible.sort()
        return compatible[0]

    def show(self, indent=0):
        if not self:
            return add_indent("No one", indent)

        lines = []
        for i in self:
            lines.append(add_indent(i, indent))
        return str.join('\n', lines)


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


def get_class(something):
    if inspect.isclass(something):
        return something
    else:
        return something.__class__


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
            raise TypeError("%s.%s" % (self.get_class(), e))

    def assert_has_method(self, name):
        if not hasattr(self.collaborator, name):
            reason = "'%s' object has no attribute '%s'" % \
                (self.collaborator_classname(), name)
            raise AttributeError(reason)

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
        if ANY_ARG in args:
            return

        if self.proxy.isclass():
            args = (None,) + args  # self

        getcallargs(self.method, *args, **kargs)

    def __repr__(self):
        return "%s.%s%s" % (self._proxy.collaborator_classname(),
                            self.name,
                            inspect.formatargspec(*self.argspec))


class Observable(object):
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, *args, **kargs):
        for ob in self.observers:
            ob(*args, **kargs)


class Method(Observable):
    def __init__(self, double, name):
        super(Method, self).__init__()
        self.double = double
        self.name = name

    def __call__(self, *args, **kargs):
        if not self.double._setting_up:
            self.notify(*args, **kargs)

        invocation = self.create_invocation(args, kargs)
        return self.double._manage_invocation(invocation)

    def create_invocation(self, args, kargs):
        return Invocation(self.double, self.name,
                          InvocationContext(*args, **kargs))

    def _was_called(self, context, times):
        invocation = Invocation(self.double, self.name, context)
        return self.double._was_called(invocation, times)

    def describe_to(self, description):
        pass

    def show(self, indent=0):
        return add_indent(self, indent)

    def __repr__(self):
        return "%s.%s" % (self.double._classname(), self.name)

    def show_history(self):
        method = "method '%s.%s'" % (self.double._classname(), self.name)
        invocations = self.double._get_invocations_to(self.name)
        if not invocations:
            return method + " never invoked"

        retval = method + " was invoked this way:\n"
        for i in invocations:
            retval += add_indent("%s\n" % i, 10)

        return retval


def func_returning(value=None):
    return lambda *args, **kargs: value


def func_returning_input(invocation):
    def func(*args, **kargs):
        if not args:
            raise TypeError("%s has no input args" % invocation)
        return args[0]

    return func


def func_raising(e):
    def raise_(e):
        raise e

    return lambda *args, **kargs: raise_(e)


@total_ordering
class Invocation(object):
    def __init__(self, double, name, context):
        self.double = double
        self.name = name
        self.context = context

    def delegates(self, delegate):
        if callable(delegate):
            self.context.delegate = delegate
            return

        try:
            self.context.delegate = iter(delegate).next
        except TypeError:
            reason = "delegates() must be called with callable or iterable instance (got '%s' instead)" % delegate
            raise WrongApiUsage(reason)

    def returns(self, value):
        self.context.output = value
        self.delegates(func_returning(value))
        return self

    def returns_input(self):
        if not self.context.args:
            raise TypeError("%s has no input args" % self)

        self.delegates(func_returning_input(self))
        return self

    def raises(self, e):
        self.delegates(func_raising(e))

    def times(self, n):
        if n < 1:
            raise WrongApiUsage("times must be >= 1. Use is_not(called()) for 0 times")

        for i in range(1, n):
            self.double._manage_invocation(self)

    def perform(self, actual_invocation):
        return self.context.exec_delegate(actual_invocation.context)

    def __eq__(self, other):
        return self.double._proxy.same_method(self.name, other.name) and \
            self.context.matches(other.context)

    def __lt__(self, other):
        if ANY_ARG in other.context.args:
            return True

        if self.name < other.name:
            return True

        if self.context < other.context:
            return True

        return False

    def __repr__(self):
        return "%s.%s%s" % (self.double._classname(), self.name, self.context)

    def show(self, indent=0):
        return add_indent(self, indent)


@total_ordering
class InvocationContext(object):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.output = None
        self.delegate = func_returning(None)

    def matches(self, other):
        try:
            if self._assert_args_match(self.args, other.args) is ANY_ARG:
                return True

            self._assert_kargs_match(self.kargs, other.kargs)
            return True
        except AssertionError:
            return False

    def exec_delegate(self, context):
        return self.delegate(*context.args, **context.kargs)

    @classmethod
    def _assert_args_match(cls, args1, args2):
        for a, b in itertools.izip_longest(args1, args2, fillvalue=IMPOSSIBLE):
            if ANY_ARG in [a, b]:
                return ANY_ARG

            cls._assert_values_match(a, b)

    @classmethod
    def _assert_kargs_match(cls, kargs1, kargs2):
        assert sorted(kargs1.keys()) == sorted(kargs2.keys())
        for key in kargs1:
            cls._assert_values_match(kargs1[key], kargs2[key])

    @classmethod
    def _assert_values_match(cls, a, b):
        if isinstance(a, BaseMatcher):
            a, b = b, a

        hamcrest.assert_that(a, hamcrest.is_(b))

    def __eq__(self, other):
        return self.matches(other)

    def __lt__(self, other):
        return (self.args, self.kargs) < (other.args, other.kargs)

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


class MockBase(object):
    pass
