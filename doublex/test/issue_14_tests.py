# Thanks to Guillermo Pascual (@pasku1)

# When you spy a method that has a decorator and you want to check the
# arguments with a hamcrest matcher, it seems like matchers are
# ignored.

from functools import wraps
import unittest
from doublex import *
from hamcrest import *


class Collaborator(object):
    def simple_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapper

    @simple_decorator
    def method_with_two_arguments(self, one, two):
        pass


class ExampleTest(unittest.TestCase):
    def test_spying_a_method_with_a_decorator(self):
        collaborator = Spy(Collaborator)
        collaborator.method_with_two_arguments(1, 'foo bar')

        assert_that(collaborator.method_with_two_arguments,
                    called().with_args(1, ends_with('bar')))
