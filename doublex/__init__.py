# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect
from contextlib import contextmanager

import internal
from .exc import *
from .const import *


class Stub(object):
    def __init__(self, collaborator=None):
        self.proxy = internal.create_proxy(collaborator)
        self.recording = False
        self.stubs = internal.InvocationSet()

    def __enter__(self):
        self.recording = True
        return self

    def __exit__(self, *args):
        self.recording = False

    def invoke(self, invocation):
        self.manage_invocation(invocation)
        if not self.recording:
            return self.perform_invocation(invocation)

    def manage_invocation(self, invocation):
        self.proxy.assert_signature_matches(invocation)
        if self.recording:
            self.stubs.append(invocation)
        else:
            self.do_manage_invocation(invocation)

    def do_manage_invocation(self, invocation):
        pass

    def perform_invocation(self, invocation):
        if invocation in self.stubs:
            return self.perform_stubbed(invocation)
        else:
            return self.do_perform_invocation(invocation)

    def do_perform_invocation(self, invocation):
        return None

    def perform_stubbed(self, invocation):
        context = self.stubs.lookup(invocation).context
        if context.exception is not None:
            raise context.exception

        return context.output

    def __getattr__(self, key):
        self.proxy.assert_has_method(key)
        return internal.Method(self, key)

    def classname(self):
        name = self.proxy.collaborator_classname()
        if name is None:
            return self.__class__.__name__
        return name


class Spy(Stub):
    def __init__(self, collaborator=None):
        super(Spy, self).__init__(collaborator)
        self.invocations = []

    def do_manage_invocation(self, invocation):
        self.invocations.append(invocation)

    def was_called(self, invocation, times):
        return self.invocations.count(invocation) >= times

    def get_invocations_to(self, name):
        retval = []
        for i in self.invocations:
            if i.name == name:
                retval.append(i)

        return retval


class ProxySpy(Spy):
    def __init__(self, collaborator):
        assert not inspect.isclass(collaborator), \
            "ProxySpy argument must be an instance"
        super(ProxySpy, self).__init__(collaborator)

    def do_perform_invocation(self, invocation):
        return self.proxy.perform_invocation(invocation)


class Mock(Spy):
    def do_manage_invocation(self, invocation):
        super(Mock, self).do_manage_invocation(invocation)
        if not invocation in self.stubs:
            raise UnexpectedBehavior(self.stubs)


def called():
    return internal.MethodCalled(
        internal.InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return internal.MethodCalled(
        internal.InvocationContext(*args, **kargs))


def meets_expectations():
    return internal.MockMeetsExpectations()


def method_returning(value):
    with Stub() as stub:
        method = internal.Method(stub, 'unnamed')
        method(ANY_ARG).returns(value)
        return method


def method_raising(exception):
    with Stub() as stub:
        method = internal.Method(stub, 'unnamed')
        method(ANY_ARG).raises(exception)
        return method
