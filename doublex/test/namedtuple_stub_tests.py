from typing import NamedTuple
from unittest import TestCase

from doublex import Stub, Spy, assert_that, property_got, called
from hamcrest import is_


class NamedtupleCollaborator(NamedTuple):
    a: str
    b: int

    def method(self, arg):
        pass


class NamedtupleStubTests(TestCase):
    def test_can_stub_namedtuple(self):
        with Stub(NamedtupleCollaborator) as stub:
            stub.a.returns('hi')
            stub.method(5).returns('Nothing')

        assert_that(stub.a, is_('hi'))
        assert_that(stub.method(5), is_('Nothing'))


class NamedtupleSpyTests(TestCase):
    def test_can_spy_namedtuple(self):
        with Spy(NamedtupleCollaborator) as spy:
            spy.a.returns('hi')
            spy.method(5).returns('Nothing')

        _ = spy.a
        spy.method(5)

        assert_that(spy, property_got('a'))
        assert_that(spy.method, called().with_args(5).times(1))
