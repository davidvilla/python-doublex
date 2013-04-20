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


class Constant(str):
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self is other


ANY_ARG = Constant('ANY_ARG')
IMPOSSIBLE = Constant('IMPOSSIBLE')


def add_indent(text, indent=0):
    return "%s%s" % (' ' * indent, text)


class OperationList(list):
    def lookup(self, invocation):
        if not invocation in self:
            raise LookupError

        compatible = [i for i in self if i == invocation]
        return sorted(compatible)[0]

    def show(self, indent=0):
        if not self:
            return add_indent("No one", indent)

        lines = [add_indent(i, indent) for i in self]
        return str.join('\n', lines)

    def count(self, invocation, pred=None):
        if pred is None:
            return list.count(self, invocation)

        return sum(1 for i in self if pred(invocation, i))


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
        invocation = self._create_invocation(args, kargs)
        retval = self.double._manage_invocation(invocation)

        if not self.double._setting_up:
            self._event.set()
            self.notify(*args, **kargs)

        return retval

    def _create_invocation(self, args, kargs):
        return Invocation.from_args(self.double, self.name, args, kargs)

    @property
    def calls(self):
        if not isinstance(self.double, SpyBase):
            raise WrongApiUsage("Only Spy derivates store invocations")
        return [x.context for x in self.double._get_invocations_to(self.name)]

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
        self.delegate = func_returning(None)

    @classmethod
    def from_args(cls, double, name, args=(), kargs={}):
        return Invocation(double, name, InvocationContext(*args, **kargs))

    def delegates(self, delegate):
        if isinstance(delegate, collections.Callable):
            self.delegate = delegate
            return

        try:
            self.delegate = iter(delegate).next
        except TypeError:
            reason = "delegates() must be called with callable or iterable instance (got '%s' instead)" % delegate
            raise WrongApiUsage(reason)

    def returns(self, value):
        self.context.retval = value
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

    # FIXME: rename to apply_stub?
    def perform(self, actual_invocation):
        context = actual_invocation.context
        return self.delegate(*context.args, **context.kargs)

    def apply_on_collaborator(self):
        return self.double._proxy.perform_invocation(self)

    def __eq__(self, other):
        return self.double._proxy.same_method(self.name, other.name) and \
            self.context.matches(other.context)

    def __lt__(self, other):
        return any([ANY_ARG in other.context.args,
                    self.name < other.name,
                    self.context < other.context])

    def __repr__(self):
        return "%s.%s%s" % (self.double._classname(), self.name, self.context)

    def show(self, indent=0):
        return add_indent(self, indent)


@total_ordering
class InvocationContext(object):
    def __init__(self, *args, **kargs):
        self.update_args(args, kargs)
        self.retval = None

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
        for a, b in itertools.izip_longest(self.args, other.args, fillvalue=IMPOSSIBLE):
            if b is ANY_ARG or a < b:
                return True

        return sorted(self.kargs.items()) < sorted(other.kargs.items())

    def __str__(self):
        return str(InvocationFormatter(self))

    def __repr__(self):
        return str(self)


class InvocationFormatter(object):
    def __init__(self, context):
        self.context = context

    def __str__(self):
        arg_values = self._format_args(self.context.args)
        arg_values.extend(self._format_kargs(self.context.kargs))

        retval = "(%s)" % str.join(', ', arg_values)
        if self.context.retval is not None:
            retval += "-> %s" % repr(self.context.retval)
        return retval

    @classmethod
    def _format_args(cls, args):
        return [cls._format_value(arg) for arg in args]

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
        return str(arg)


class PropertyInvocation(Invocation):
    def __eq__(self, other):
        return self.name == other.name


class PropertyGet(PropertyInvocation):
    def __init__(self, double, name):
        super(PropertyGet, self).__init__(double, name)

    def apply_on_collaborator(self):
        return getattr(self.double._proxy.collaborator, self.name)

    def __repr__(self):
        return "get %s.%s" % (self.double._classname(), self.name)


class PropertySet(PropertyInvocation):
    def __init__(self, double, name, value):
        self.value = value
        param = InvocationContext(value)
        super(PropertySet, self).__init__(double, name, param)

    def apply_on_collaborator(self):
        return setattr(self.double._proxy.collaborator, self.name, self.value)

    def __repr__(self):
        return "set %s.%s to %s" % (self.double._classname(),
                                    self.name, self.value)


def property_factory(double, key):
    def manage(invocation):
        return double._manage_invocation(invocation)

    def get_property(obj):
        return manage(PropertyGet(double, key))

    def set_property(obj, value):
        prop = double._proxy.get_class_attr(key)
        if prop.fset is None:
            raise AttributeError("can't set attribute %s" % key)

        invocation = manage(PropertySet(double, key, value))

        if double._setting_up:
            invocation.returns(value)

    return property(get_property, set_property)


class AttributeFactory(object):
    """
    Create double methods, properties or attributes from collaborator
    """

    typemap = dict(
        instancemethod    = Method,
        method_descriptor = Method,
        property          = property_factory,
        # -- python3 --
        method            = Method,
        function          = Method,
        )

    @classmethod
    def create(cls, double, key):
        get_actual_attr = lambda double, key: double._proxy.get_attr(key)
        typename = double._proxy.get_attr_typename(key)
        attr = cls.typemap.get(typename, get_actual_attr)
        return attr(double, key)


class SpyBase(object):
    pass


class MockBase(object):
    pass
