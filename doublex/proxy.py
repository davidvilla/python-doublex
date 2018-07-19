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
import inspect

try:
    from inspect import getcallargs
except ImportError:
    from .py27_backports import getcallargs

from .internal import ANY_ARG


def get_func(func):
    if sys.version_info >= (3, 4):
        return func.__func__
    else:
        return func.im_func


def create_proxy(collaborator):
    if collaborator is None:
        return DummyProxy()

    return CollaboratorProxy(collaborator)


class Proxy(object):
    def assure_signature_matches(self, invocation):
        pass

    def collaborator_classname(self):
        return None

    def get_signature(self, method_name):
        if self.is_property(method_name):
            return PropertySignature(self, method_name)

        if not self.is_method_or_func(method_name):
            return BuiltinSignature(self, method_name)

        return MethodSignature(self, method_name)

    def is_property(self, attr_name):
        attr = getattr(self.collaborator_class, attr_name)
        return isinstance(attr, property)

    def is_method_or_func(self, method_name):
        func = getattr(self.collaborator, method_name)
        if inspect.ismethod(func):
            func = get_func(func)
            # func = func.im_func
        return inspect.isfunction(func)


class DummyProxy(Proxy):
    def get_attr_typename(self, key):
        return 'instancemethod'

    def same_method(self, name1, name2):
        return name1 == name2

    def get_signature(self, method_name):
        return DummySignature()


def get_class(something):
    if inspect.isclass(something):
        return something
    else:
        return something.__class__


class CollaboratorProxy(Proxy):
    '''Represent the collaborator object'''
    def __init__(self, collaborator):
        self.collaborator = collaborator
        self.collaborator_class = get_class(collaborator)

    def isclass(self):
        return inspect.isclass(self.collaborator)

    def get_class_attr(self, key):
        return getattr(self.collaborator_class, key)

    def get_attr(self, key):
        return getattr(self.collaborator, key)

    def collaborator_classname(self):
        return self.collaborator_class.__name__

    def assure_signature_matches(self, invocation):
        signature = self.get_signature(invocation.name)
        signature.assure_matches(invocation.context)

    def get_attr_typename(self, key):
        def raise_no_attribute():
            reason = "'%s' object has no attribute '%s'" % \
                (self.collaborator_classname(), key)
            raise AttributeError(reason)

        try:
            attr = getattr(self.collaborator_class, key)
            return type(attr).__name__
        except AttributeError:
            if self.collaborator is self.collaborator_class:
                raise_no_attribute()

        try:
            attr = getattr(self.collaborator, key)
            return type(attr).__name__
        except AttributeError:
            raise_no_attribute()

    def same_method(self, name1, name2):
        return getattr(self.collaborator, name1) == \
            getattr(self.collaborator, name2)

    def perform_invocation(self, invocation):
        method = getattr(self.collaborator, invocation.name)
        return invocation.context.apply_on(method)


class Signature(object):
    def __init__(self, proxy, name):
        self.proxy = proxy
        self.name = name
        self.method = getattr(proxy.collaborator, name)

    def get_arg_spec(self):
        pass

    def get_call_args(self, context):
        retval = context.kargs.copy()
        for n, i in enumerate(context.args):
            retval['_positional_%s' % n] = i

        return retval

    def __eq__(self, other):
        return (self.proxy, self.name, self.method) == \
            (other.proxy, other.name, other.method)


class DummySignature(Signature):
    def __init__(self):
        pass


class BuiltinSignature(Signature):
    "builtin collaborator method signature"
    def assure_matches(self, context):
        doc = self.method.__doc__
        if not ')' in doc:
            return

        rpar = doc.find(')')
        params = doc[:rpar]
        nkargs = params.count('=')
        nargs = params.count(',') + 1 - nkargs
        if len(context.args) != nargs:
            raise TypeError('%s.%s() takes exactly %s argument (%s given)' % (
                self.proxy.collaborator_classname(), self.name,
                nargs, len(context.args)))


# Thanks to David Pärsson (https://github.com/davidparsson)
# issue: https://bitbucket.org/DavidVilla/python-doublex/issues/25/support-from-python-35-type-hints-when
def getfullargspec(method):
    try:
        return inspect.getargspec(method)
    except ValueError:
        return inspect.getfullargspec(method)


class MethodSignature(Signature):
    "colaborator method signature"
    def __init__(self, proxy, name):
        super(MethodSignature, self).__init__(proxy, name)
        self.argspec = getfullargspec(self.method)

    def get_arg_spec(self):
        retval = inspect.getargspec(self.method)
        del retval.args[0]
        return retval

    def get_call_args(self, context):
        args = context.args
        if self.proxy.isclass():
            args = (None,) + args  # self

        retval = getcallargs(self.method, *args, **context.kargs)
        del retval['self']
        return retval

    def assure_matches(self, context):
        if ANY_ARG in context.args:
            return

        try:
            self.get_call_args(context)
        except TypeError as e:
            raise TypeError("%s.%s" % (self.proxy.collaborator_classname(), e))

    def __repr__(self):
        return "%s.%s%s" % (self.proxy.collaborator_classname(),
                            self.name,
                            inspect.formatargspec(*self.argspec))


class PropertySignature(Signature):
    def __init__(self, proxy, name):
        pass

    def assure_matches(self, context):
        pass
