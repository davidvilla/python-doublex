# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect
from contextlib import contextmanager

import internal
from .exc import *
from .const import *


class Stub(object):
    def __init__(self, collaborator=None):
        self.proxy = internal.create_proxy(collaborator)
        self.ready()
        self.stubbed_invocations = []

    def record(self):
        self.recording = True

    def ready(self):
        self.recording = False

    def invoke(self, invocation):
        self.proxy.assert_match_signature(invocation)
        if self.recording:
            self.stubbed_invocations.append(invocation)
        else:
            return self.do_invoke(invocation)

    def do_invoke(self):
        raise NotImplementedError

    def lookup_stub_invocation(self, invocation):
        i = self.stubbed_invocations.index(invocation)
        return self.stubbed_invocations[i]

    def __getattr__(self, key):
        self.proxy.assert_has_method(key)

        method = self.create_method(key)
        setattr(self, key, method)
        return method

    def create_method(self, name):
        return internal.StubbedMethod(self, name)


class Spy(Stub):
    def __init__(self, collaborator=None):
        super(Spy, self).__init__(collaborator)
        self.invocations = []

    def do_invoke(self, invocation):
        self.invocations.append(invocation)

    def was_called(self, invocation, times):
        return self.invocations.count(invocation) >= times

    def get_invocations_to(self, name):
        retval = []
        for i in self.invocations:
            if i.name == name:
                retval.append(i)

        return retval

    def create_method(self, name):
        return internal.SpiedMethod(self, name)


class ProxySpy(Spy):
    def __init__(self, collaborator):
        assert not inspect.isclass(collaborator), \
            "ProxySpy argument must be an instance"
        super(ProxySpy, self).__init__(collaborator)

    def do_invoke(self, invocation):
        super(ProxySpy, self).do_invoke(invocation)
        return self.proxy.perform_invocation(invocation)


def called():
    return internal.MethodCalled(
        internal.InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return internal.MethodCalled(
        internal.InvocationContext(*args, **kargs))


@contextmanager
def record(double):
    double.record()
    yield
    double.ready()
