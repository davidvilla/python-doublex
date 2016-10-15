from unittest import TestCase
from doublex import Stub


# new on 1.8.3
# issue: https://bitbucket.org/DavidVilla/python-doublex/issues/25/support-from-python-35-type-hints-when
class TypeHintTests(TestCase):
    def test_returning_type_hint(self):
        class MyClass:
            def get_name(self) -> str:
                return 'a name'

        with Stub(MyClass) as my_class:
            my_class.get_name().returns('another name')
