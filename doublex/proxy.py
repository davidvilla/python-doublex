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
    from py27_backports import getcallargs

from .internal import ANY_ARG


def create_proxy(collaborator):
    if collaborator is None:
        return DummyProxy()

    return Proxy(collaborator)


class DummyProxy(object):
    def get_attr_typeid(self, key):
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

    def get_attr_typeid(self, key):
        try:
            return type(getattr(self.collaborator, key)).__name__
        except AttributeError:
            reason = "'%s' object has no attribute '%s'" % \
                (self.collaborator_classname(), key)
            raise AttributeError(reason)

    def collaborator_classname(self):
        return self.collaborator_class.__name__

    def assure_signature_matches(self, invocation):
        assert self.get_attr_typeid(invocation.name) == 'instancemethod'

        signature = Signature(self, invocation.name)
        try:
            signature.assure_match(invocation.context.args,
                                   invocation.context.kargs)
        except TypeError, e:
            raise TypeError("%s.%s" % (self.collaborator_class, e))

    def same_method(self, name1, name2):
        return getattr(self.collaborator, name1) == \
            getattr(self.collaborator, name2)

    def perform_invocation(self, invocation):
        method = getattr(self.collaborator, invocation.name)
        return method(*invocation.context.args,
                       **invocation.context.kargs)


def create_signature(proxy, method_name):
    method = getattr(proxy.collaborator, method_name)
    if not inspect.isfunction(method):
        return DummySignature(method)

    return Signature(method)


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

    def assure_match(self, args, kargs):
        if ANY_ARG in args:
            return

        if self.proxy.isclass():
            args = (None,) + args  # self

        getcallargs(self.method, *args, **kargs)

    def __repr__(self):
        return "%s.%s%s" % (self._proxy.collaborator_classname(),
                            self.name,
                            inspect.formatargspec(*self.argspec))
