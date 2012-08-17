# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect

import hamcrest

from .internal import ANY_ARG, create_proxy, InvocationSet, Method, MockBase
from .matchers import MockExpectInvocation


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
            stubbed = self.stubs.lookup(invocation)
            return stubbed.perform(invocation)

        return self.perform_invocation(invocation)

    def do_manage_invocation(self, invocation):
        pass

    def perform_invocation(self, invocation):
        return None

    def __getattr__(self, key):
        self.proxy.assert_has_method(key)
        method = Method(self, key)
        setattr(self, key, method)
        return method

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
        try:
            hamcrest.assert_that(self.invocations.count(invocation),
                                 hamcrest.is_(times))
            return True
        except AssertionError:
            return False

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


class Mock(Spy, MockBase):
    def do_manage_invocation(self, invocation):
        super(Mock, self).do_manage_invocation(invocation)
        hamcrest.assert_that(self, MockExpectInvocation(invocation))


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
