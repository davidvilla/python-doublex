from unittest import TestCase

from doublex import Stub, Spy, when
from hamcrest import assert_that, anything, is_


class CollaboratorWithProperty:
    @property
    def prop(self):
        pass


class Collaborator:
    def method_accepting_property(self, prop):
        pass


class AnyArgTests(TestCase):
    def test_any_arg_matches_property(self):
        prop_stub = Spy(CollaboratorWithProperty)
        when(prop_stub).prop.returns(5)

        with Stub(Collaborator) as stub:
            stub.method_accepting_property(prop=anything()).returns(2)

        assert_that(stub.method_accepting_property(prop_stub.prop), is_(2))
        assert prop_stub.prop == 5
