# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect

from .internal import ANY_ARG, create_proxy, \
    InvocationSet, InvocationContext, \
    Method, MethodCalled, MockMeetsExpectations
from .exc import *


class Stub(object):
    def __init__(self, collaborator=None):
        self.proxy = create_proxy(collaborator)
        self.stubs = InvocationSet()
        self.recording = False

    def __enter__(self):
        self.recording = True
        return self

    def __exit__(self, *args):
        self.recording = False

    def manage_invocation(self, invocation):
        self.proxy.assert_signature_matches(invocation)
        if self.recording:
            self.stubs.append(invocation)
            return

        self.do_manage_invocation(invocation)

        if invocation in self.stubs:
            return self.stubs.lookup(invocation).perform()

        return self.perform_invocation(invocation)

    def do_manage_invocation(self, invocation):
        pass

    def perform_invocation(self, invocation):
        return None

    def __getattr__(self, key):
        self.proxy.assert_has_method(key)
        return Method(self, key)

    def classname(self):
        name = self.proxy.collaborator_classname()
        if name is None:
            return self.__class__.__name__
        return name


class Spy(Stub):
    def __init__(self, collaborator=None):
        super(Spy, self).__init__(collaborator)
        self.invocations = InvocationSet()

    def do_manage_invocation(self, invocation):
        self.invocations.append(invocation)

    def was_called(self, invocation, times):
        return self.invocations.count(invocation) >= times

    def get_invocations_to(self, name):
        return [i for i in self.invocations
                if self.proxy.same_method(name, i.name)]


class ProxySpy(Spy):
    def __init__(self, collaborator):
        assert not inspect.isclass(collaborator), \
            "ProxySpy argument must be an instance"
        super(ProxySpy, self).__init__(collaborator)

    def perform_invocation(self, invocation):
        return self.proxy.perform_invocation(invocation)


class Mock(Spy):
    def do_manage_invocation(self, invocation):
        super(Mock, self).do_manage_invocation(invocation)
        if not invocation in self.stubs:
            raise UnexpectedBehavior(self.stubs)


def called():
    return MethodCalled(InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return MethodCalled(InvocationContext(*args, **kargs))


def meets_expectations():
    return MockMeetsExpectations()


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
