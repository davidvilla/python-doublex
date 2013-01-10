# -*- coding:utf-8; tab-width:4; mode:python -*-

# doublex
#
# Copyright © 2012 David Villa Alises
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


import inspect

try:
    from inspect import getcallargs
except ImportError:
    from .py27_backports import getcallargs

from .internal import ANY_ARG


def create_proxy(collaborator):
    if collaborator is None:
        return DummyProxy()

    return Proxy(collaborator)


class DummyProxy(object):
    def get_attr_typename(self, key):
        return 'instancemethod'

    def assure_signature_matches(self, invocation):
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
        signature = create_signature(self, invocation.name)
        signature.assure_match(invocation.context.args,
                               invocation.context.kargs)

    def get_attr_typename(self, key):
        try:
            attr = getattr(self.collaborator, key)
            return type(attr).__name__
        except AttributeError:
            reason = "'%s' object has no attribute '%s'" % \
                (self.collaborator_classname(), key)
            raise AttributeError(reason)

    def same_method(self, name1, name2):
        return getattr(self.collaborator, name1) == \
            getattr(self.collaborator, name2)

    def perform_invocation(self, invocation):
        method = getattr(self.collaborator, invocation.name)
        return method(*invocation.context.args,
                       **invocation.context.kargs)


def create_signature(proxy, method_name):
    method = getattr(proxy.collaborator, method_name)
    if not is_method_or_func(method):
        return BuiltinSignature(proxy, method_name)

    return Signature(proxy, method_name)


def is_method_or_func(func):
    if inspect.ismethod(func):
        func = func.im_func
    return inspect.isfunction(func)


class BuiltinSignature(object):
    "builtin collaborator method signature"
    def __init__(self, proxy, name):
        self.proxy = proxy
        self.name = name
        self.method = getattr(proxy.collaborator, name)

    def assure_match(self, args, kargs):
        doc = self.method.__doc__
        if not ')' in doc:
            return

        rpar = doc.find(')')
        params = doc[:rpar]
        nkargs = params.count('=')
        nargs = params.count(',') + 1 - nkargs
        if len(args) != nargs:
            raise TypeError('%s.%s() takes exactly %s argument (%s given)' % (
                    self.proxy.collaborator_classname(), self.name, nargs, len(args)))


class Signature(object):
    "colaborator method signature"
    def __init__(self, proxy, name):
        self.proxy = proxy
        self.name = name
        self.method = getattr(proxy.collaborator, name)
        self.argspec = inspect.getargspec(self.method)

    def assure_match(self, args, kargs):
        if ANY_ARG in args:
            return

        if self.proxy.isclass():
            args = (None,) + args  # self

        try:
            getcallargs(self.method, *args, **kargs)
        except TypeError as e:
            raise TypeError("%s.%s" % (self.proxy.collaborator_classname(), e))

    def __repr__(self):
        return "%s.%s%s" % (self._proxy.collaborator_classname(),
                            self.name,
                            inspect.formatargspec(*self.argspec))
