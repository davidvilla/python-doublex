# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect
import itertools

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher

import safeunicode
from .exc import *


class SingleValue:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


ANY_ARG = SingleValue('ANY_ARG')
IMPOSSIBLE = SingleValue('IMPOSSIBLE')


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
        if self.proxy.isclass():
            args = (None,) + args  # self

        # This requires python-2.7!!!
        inspect.getcallargs(self.method, *args, **kargs)

#    def __repr__(self):
#        return "%s.%s%s" % (self.proxy.collaborator_classname(),
#                            self.name,
#                            inspect.formatargspec(*self.argspec))


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
        invocation = self.create_invocation(args, kargs)
        retval = self.double.manage_invocation(invocation)

        if self.double.recording:
            return invocation

        self.notify(*args, **kargs)
        return retval

    def create_invocation(self, args, kargs):
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

    def delegates(self, delegate):
        if callable(delegate):
            self.context.delegate = delegate
            return

        try:
            self.context.delegate = iter(delegate).next
        except TypeError:
            raise WrongApiUsage("delegates() arg must be callable or iterable object")

    def returns(self, value):
        self.delegates(lambda *args, **kargs: value)
        return self

    def returns_input(self):
        if not self.context.args:
            raise TypeError("%s has no input args" % self)

        self.returns(self.context.args)
        return self

    def raises(self, value):
        def raise_exc(e):
            raise e

        self.delegates(lambda *args, **kargs: raise_exc(value))

    def times(self, n):
        if n < 1:
            raise WrongApiUsage("times must be >= 1. Use is_not(called()) for 0 times")

        for i in range(1, n):
            self.double.manage_invocation(self)

    def perform(self):
        return self.context.delegate(*self.context.args, **self.context.kargs)

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
        self.delegate = lambda *args, **kargs: None

    def matches(self, other):
        try:
            if self._assert_args_match(self.args, other.args) is ANY_ARG:
                return True

            self._assert_kargs_match(self.kargs, other.kargs)
            return True
        except AssertionError:
            return False

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
