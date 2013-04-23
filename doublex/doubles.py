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

import hamcrest

from .internal import (ANY_ARG, OperationList, Method, MockBase, SpyBase,
                       AttributeFactory)
from .proxy import create_proxy, get_class
from .matchers import MockIsExpectedInvocation


__all__ = ['Stub', 'Spy', 'ProxySpy', 'Mock', 'Mimic',
           'method_returning', 'method_raising',
           'ANY_ARG']


class Stub(object):
    def __new__(cls, collaborator=None):
        '''Creates a fresh class clone per instance. This is required due to
        ad-hoc stub properties are class attributes'''
        klass = type(cls.__name__, (cls,), dict(cls.__dict__))
        return object.__new__(klass)

    def __init__(self, collaborator=None):
        self._proxy = create_proxy(collaborator)
        self._stubs = OperationList()
        self._setting_up = False
        self.__class__.__setattr__ = self.__setattr__hook

    def __enter__(self):
        self._setting_up = True
        return self

    def __exit__(self, *args):
        self._setting_up = False

    def _manage_invocation(self, invocation):
        self._proxy.assure_signature_matches(invocation)

        if self._setting_up:
            self._stubs.append(invocation)
            return invocation

        self._prepare_invocation(invocation)

        stubbed_retval = None
        if invocation in self._stubs:
            stubbed = self._stubs.lookup(invocation)
            stubbed_retval = stubbed.perform(invocation)

        actual_retval = self._perform_invocation(invocation)

        retval = stubbed_retval if stubbed_retval is not None else actual_retval
        invocation.context.retval = retval
        return retval

    def _prepare_invocation(self, invocation):
        pass

    def _perform_invocation(self, invocation):
        return None

    def __getattr__(self, key):
        self._add_attr_from_collaborator(key)
        return object.__getattribute__(self, key)

    def __setattr__hook(self, key, value):
        if key in self.__dict__:
            object.__setattr__(self, key, value)
            return

        try:
            self._add_attr_from_collaborator(key)
        except AttributeError:
            #  collaborator has not attribute 'key', creaing it ad-hoc
            pass

        # descriptor protocol compliant
        object.__setattr__(self, key, value)

    def _add_attr_from_collaborator(self, key):
        attr = AttributeFactory.create(self, key)
        if isinstance(attr, property):
            setattr(self.__class__, key, attr)
        else:
            object.__setattr__(self, key, attr)

    def _classname(self):
        name = self._proxy.collaborator_classname()
        return name or self.__class__.__name__


class Spy(Stub, SpyBase):
    def __init__(self, collaborator=None):
        self._recorded = OperationList()
        super(Spy, self).__init__(collaborator)

    def _prepare_invocation(self, invocation):
        self._recorded.append(invocation)

    def _received_invocation(self, invocation, times, cmp_pred=None):
        return hamcrest.is_(times).matches(
            self._recorded.count(invocation, cmp_pred))

    def _get_invocations_to(self, name):
        return [i for i in self._recorded
                if self._proxy.same_method(name, i.name)]


class ProxySpy(Spy):
    def __init__(self, collaborator):
        self._assure_is_instance(collaborator)
        super(ProxySpy, self).__init__(collaborator)

    def _assure_is_instance(self, thing):
        if thing is None or inspect.isclass(thing):
            raise TypeError("ProxySpy takes an instance (got %s instead)" % thing)

    def _perform_invocation(self, invocation):
        return invocation.apply_on_collaborator()


class Mock(Spy, MockBase):
    def _prepare_invocation(self, invocation):
        hamcrest.assert_that(self, MockIsExpectedInvocation(invocation))
        super(Mock, self)._prepare_invocation(invocation)


def Mimic(double, collab):
    def __getattribute__hook(self, key):
        if key in ['__class__', '__dict__',
                   '_get_method', '_methods'] or \
                key in [x[0] for x in inspect.getmembers(double)] or \
                key in self.__dict__:
            return object.__getattribute__(self, key)

        return self._get_method(key)

    def _get_method(self, key):
        if key not in list(self._methods.keys()):
            typename = self._proxy.get_attr_typename(key)
            assert typename in ['instancemethod', 'function', 'method'], typename
            method = Method(self, key)
            self._methods[key] = method

        return self._methods[key]

    assert issubclass(double, Stub), \
        "Mimic() takes a double class as first argument (got %s instead)" & double

    collab_class = get_class(collab)
    generated_class = type(
        "Mimic_%s_for_%s" % (double.__name__, collab_class.__name__),
        (double, collab_class) + collab_class.__bases__,
        dict(_methods = {},
             __getattribute__ = __getattribute__hook,
             _get_method = _get_method))
    return generated_class(collab)


def method_returning(value):
    with Stub() as stub:
        method = Method(stub, 'unnamed')
        method(ANY_ARG).returns(value)
        return method


def method_raising(exception):
    with Stub() as stub:
        method = Method(stub, 'unnamed')
        method(ANY_ARG).raises(exception)
        return method
