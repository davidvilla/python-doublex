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


import itertools
import threading
import collections

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher

try:
    from functools import total_ordering
except ImportError:
    from .py27_backports import total_ordering


from .safeunicode import get_string


class WrongApiUsage(Exception):
    pass


class SingleValue:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return id(self) == id(other)


ANY_ARG = SingleValue('ANY_ARG')
IMPOSSIBLE = SingleValue('IMPOSSIBLE')


def add_indent(text, indent=0):
    return "%s%s" % (' ' * indent, text)


class OperationList(list):
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
        self._event = threading.Event()

    def __call__(self, *args, **kargs):
        if not self.double._setting_up:
            self.notify(*args, **kargs)

        self._event.set()

        invocation = self.create_invocation(args, kargs)
        return self.double._manage_invocation(invocation)

    def create_invocation(self, args, kargs):
        return Invocation.from_args(self.double, self.name, args, kargs)

    def _was_called(self, context, times):
        invocation = Invocation(self.double, self.name, context)
        return self.double._received_invocation(invocation, times)

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
    def __init__(self, double, name, context=None):
        self.double = double
        self.name = name
        self.context = context or InvocationContext()

    @classmethod
    def from_args(cls, double, name, args=(), kargs={}):
        return Invocation(double, name, InvocationContext(*args, **kargs))

    def delegates(self, delegate):
        if isinstance(delegate, collections.Callable):
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
        return "%s.%s%s" % (self.double._classname(),
                            self.name, self.context)

    def show(self, indent=0):
        return add_indent(self, indent)


@total_ordering
class InvocationContext(object):
    def __init__(self, *args, **kargs):
        self.update_args(args, kargs)
        self.output = None
        self.delegate = func_returning(None)

    def update_args(self, args, kargs):
        self.args = args
        self.kargs = kargs

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
        return (self.args, sorted(self.kargs.items())) < \
            (other.args, sorted(other.kargs.items()))

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

    @classmethod
    def _format_args(cls, args):
        items = []
        for arg in args:
            items.append(cls._format_value(arg))

        return items

    @classmethod
    def _format_kargs(cls, kargs):
        return ['%s=%s' % (key, cls._format_value(val))
                for key, val in sorted(kargs.items())]

    @classmethod
    def _format_value(cls, arg):
        if isinstance(arg, unicode):
            arg = get_string(arg)

        if isinstance(arg, (int, str, dict)):
            return repr(arg)
        else:
            return str(arg)


class PropertyGet(Invocation):
    def __repr__(self):
        return "get %s.%s" % (self.double._classname(), self.name)


class PropertySet(Invocation):
    def __init__(self, double, name, value=None):
        super(PropertySet, self).__init__(
            double, name, InvocationContext(value))
        self.value = value

    def _was_called(self, times):
        return self.double._was_called(self, times)

    def __repr__(self):
        return "set %s.%s to %s" % (
            self.double._classname(), self.name, self.value)


class Property(object):
    def __init__(self, double, key):
        self.double = double
        self.key = key
        self.value = None

    def __get__(self, obj, type=None):
        self._manage(PropertyGet(self.double, self.key))
        return self.value

    def __set__(self, obj, value):
        prop = self.double._proxy.get_class_attr(self.key)
        if prop.fset is None:
            raise AttributeError("can't set attribute")

        self._manage(PropertySet(self.double, self.key, value))
        self.value = value

    def _manage(self, operation):
        self.double._manage_invocation(operation, check=False)


class AttributeFactory(object):
    typemap = {
        'instancemethod':    Method,
        'method_descriptor': Method,
        'property':          Property,
        # -- python3 --
        'method':            Method,
        'function':          Method,
        }

    @classmethod
    def create(cls, double, key):
        typename = double._proxy.get_attr_typename(key)
        return cls.typemap[typename](double, key)


class SpyBase(object):
    pass


class MockBase(object):
    pass
