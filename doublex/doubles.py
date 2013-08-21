# -*- coding:utf-8; tab-width:4; mode:python -*-

# doublex
#
# Copyright © 2012, 2013 David Villa Alises
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


class StubManager(object):
    '''StubManager extract framework API from Stubs'''

    def __init__(self, double, collaborator):
        self.double = double
        self.proxy = create_proxy(collaborator)
        self.stubs = OperationList()
        self.setting_up = False

    def manage_invocation(self, invocation):
        self.proxy.assure_signature_matches(invocation)

        if self.setting_up:
            self.stubs.append(invocation)
            return invocation

        self.prepare_invocation(invocation)

        stubbed_retval = self.double._default_behavior()
        if invocation in self.stubs:
            stubbed = self.stubs.lookup(invocation)
            stubbed_retval = stubbed._apply_stub(invocation)

        actual_retval = self.perform_invocation(invocation)

        retval = stubbed_retval if stubbed_retval is not None else actual_retval
        invocation._context.retval = retval
        return retval

    def prepare_invocation(self, invocation):
        pass

    def perform_invocation(self, invocation):
        return None

    def classname(self):
        name = self.proxy.collaborator_classname()
        return name or self.double.__class__.__name__


class Stub(object):
    _default_behavior = lambda x: None

    def __new__(cls, collaborator=None):
        '''Creates a fresh class clone per instance. This is required due to
        ad-hoc stub properties are class attributes'''
        klass = cls._clone_class()
        return object.__new__(klass)

    @classmethod
    def _clone_class(cls):
        return type(cls.__name__, (cls,), dict(cls.__dict__))

    def __init__(self, collaborator=None):
        object.__setattr__(self, '_doublex', StubManager(self, collaborator))

    def __enter__(self):
        self._doublex.setting_up = True
        return self

    def __exit__(self, *args):
        self._doublex.setting_up = False

    def __getattr__(self, key):
        AttributeFactory.create(self, key)
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if key in self.__dict__:
            object.__setattr__(self, key, value)
            return

        try:
            AttributeFactory.create(self, key)
        except AttributeError:
            #  collaborator has not attribute 'key', creaing it ad-hoc
            pass

        # descriptor protocol compliant
        object.__setattr__(self, key, value)


class SpyManager(StubManager):
    def __init__(self, spy, collaborator=None):
        self.recorded = OperationList()
        super(SpyManager, self).__init__(spy, collaborator)

    def prepare_invocation(self, invocation):
        self.recorded.append(invocation)

    def received_invocation(self, invocation, times, cmp_pred=None):
        return hamcrest.is_(times).matches(
            self.recorded.count(invocation, cmp_pred))

    def get_invocations_to(self, name):
        return [i for i in self.recorded
                if self.proxy.same_method(name, i._name)]


class Spy(Stub, SpyBase):
    def __init__(self, collaborator=None):
        object.__setattr__(self, '_doublex', SpyManager(self, collaborator))


class ProxySpyManager(SpyManager):
    def assure_is_instance(self, thing):
        if thing is None or inspect.isclass(thing):
            raise TypeError("ProxySpy takes an instance (got %s instead)" % thing)

    def perform_invocation(self, invocation):
        return invocation._apply_on_collaborator()


class ProxySpy(Spy):
    def __init__(self, collaborator=None):
        object.__setattr__(self, '_doublex', ProxySpyManager(self, collaborator))
        self._doublex.assure_is_instance(collaborator)


class MockManager(SpyManager):
    def prepare_invocation(self, invocation):
        hamcrest.assert_that(self.double, MockIsExpectedInvocation(invocation))
        super(MockManager, self).prepare_invocation(invocation)


class Mock(Spy, MockBase):
    def __init__(self, collaborator=None):
        object.__setattr__(self, '_doublex', MockManager(self, collaborator))


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
            typename = self._doublex.proxy.get_attr_typename(key)
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
        method = Method(stub, 'orphan')
        method(ANY_ARG).returns(value)
        return method


def method_raising(exception):
    with Stub() as stub:
        method = Method(stub, 'orphan')
        method(ANY_ARG).raises(exception)
        return method
