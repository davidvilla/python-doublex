from unittest import TestCase

from doublex import Stub, Spy, when, called, ANY_ARG
from hamcrest import assert_that, anything, is_, instance_of


class CollaboratorWithProperty:
    @property
    def prop(self):
        pass


class Collaborator:
    def method_accepting_property(self, prop):
        pass


class RaisingEq:
    def __eq__(self, other):
        raise ValueError('I dont like comparisons')


class AnyArgTests(TestCase):
    def test_any_arg_matches_property(self):
        prop_stub = Spy(CollaboratorWithProperty)
        when(prop_stub).prop.returns(5)

        with Stub(Collaborator) as stub:
            stub.method_accepting_property(prop=anything()).returns(2)

        assert_that(stub.method_accepting_property(prop_stub.prop), is_(2))
        assert prop_stub.prop == 5

    def test_any_arg_checking_works_when_eq_raises(self):
        with Spy(Collaborator) as spy:
            spy.method_accepting_property(ANY_ARG).returns(6)

        assert_that(spy.method_accepting_property(RaisingEq()), is_(6))
        assert_that(spy.method_accepting_property, called().with_args(instance_of(RaisingEq)))
