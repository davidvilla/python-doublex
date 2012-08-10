# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase

from hamcrest import assert_that, is_not
from doublex import Spy, called, called_with, ApiMismatch, ANY_ARG


class EmptySpyTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_simple_invocation(self):
        self.spy.foo()

    def test_called(self):
        self.spy.foo()

        assert_that(self.spy.foo, called())

    def test_not_called(self):
        self.spy.foo()

        assert_that(self.spy.bar, is_not(called()))

    def test_called_2_times(self):
        self.spy.foo()
        self.spy.foo()

        assert_that(self.spy.foo, called().times(2))
        assert_that(self.spy.foo, is_not(called().times(3)))

    def test_called_without_args(self):
        self.spy.foo()

        assert_that(self.spy.foo, called_with())

    def test_not_called_without_args(self):
        self.spy.foo(1)

        assert_that(self.spy.foo, is_not(called_with()))

    def test_called_with_specified_args(self):
        self.spy.foo(1)

        assert_that(self.spy.foo, called_with(1))

    def test_not_called_with_specified_args(self):
        self.spy.foo()
        self.spy.foo(2)

        assert_that(self.spy.foo, is_not(called_with(1)))

    def test__called__and__called_with__any_args_is_the_same(self):
        self.spy.foo()
        self.spy.foo(3)
        self.spy.foo('hi')
        self.spy.foo(None)

        assert_that(self.spy.foo, called().times(4))
        assert_that(self.spy.foo, called_with(ANY_ARG).times(4))

    def test_called_with_several_types_and_kargs(self):
        self.spy.foo(3.0, [1, 2], 'hi', color='red', width=10)

        assert_that(self.spy.foo, called_with(
                3.0, [1, 2], 'hi', color='red', width=10))
        assert_that(self.spy.foo, called_with(
                3.0, [1, 2], 'hi', width=10, color='red'))
        assert_that(self.spy.foo, is_not(called_with(
                [1, 2], 'hi', width=10, color='red')))
        assert_that(self.spy.foo, is_not(called_with(
                [1, 2], 3.0, 'hi', width=10, color='red')))

    def test_called_with_args_and_times(self):
        self.spy.foo(1)
        self.spy.foo(1)
        self.spy.foo(2)

        assert_that(self.spy.foo, called_with(1).times(2))
        assert_that(self.spy.foo, called_with(2))
        assert_that(self.spy.foo, called().times(3))


class VerifiedSpyTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator())

    def test_call_unexisting_method(self):
        try:
            self.spy.wrong()
            self.fail('ApiMismatch should be raised')
        except ApiMismatch as e:
            self.assertIn(str(e), "No such method: Collaborator.wrong")

    def test_check_unexisting_method(self):
        try:
            assert_that(self.spy.wrong, called())
            self.fail('ApiMismatch should be raised')
        except ApiMismatch as e:
            self.assertIn(str(e), "No such method: Collaborator.wrong")

    def test_create_from_oldstyle_class(self):
        self.spy = Spy(Collaborator)

    def test_create_from_newstyle_class(self):
        class Actor(object):
            pass

        self.spy = Spy(Actor)




#----------------------------#
#- pyDoubles migrated tests -#
#----------------------------#

class Collaborator:
    """
    The original object we double in tests
    """
    test_field = "OK"

    def hello(self):
        return "hello"

    def something(self):
        return "ok"

    def one_arg_method(self, arg1):
        return arg1

    def two_args_method(self, arg1, arg2):
        return arg1 + arg2

    def kwarg_method(self, key_param=False):
        return key_param

    def mixed_method(self, arg1, key_param=False):
        return key_param + arg1

    def void_method(self):
        pass

    def method_one(self, arg1):
        return 1

    alias_method = one_arg_method


class pyDoublesSpyTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator())

    def test_override_original_method(self):
        self.assertTrue(self.spy.hello() is None)

    def test_override_original_method_and_is_called(self):
        self.spy.hello()
        assert_that(self.spy.hello, called())

    def test_spy_without_args_is_empty_spy(self):
        self.spy = Spy()
        self.assertTrue(self.spy.hello() is None)

    def test_spy_can_work_from_empty_and_is_called(self):
        self.spy.hello()
        assert_that(self.spy.hello, called())

    def test_spy_based_on_object_must_check_api_match(self):
        try:
            self.spy.hello("unexpected argument")
            self.fail('Expection should raise: Actual objet does not accept parameters')
        except ApiMismatch:
            pass

    def test_check_api_match_with_kwargs(self):
        self.assertTrue(self.spy.mixed_method(1, key_param=2) is None)

    def test_check_api_match_with_kwargs_not_used(self):
        self.assertTrue(self.spy.mixed_method(1) is None)

    def test_check_api_match_with_kwargs_not_matching(self):
        try:
            self.spy.mixed_method(1, 2, 3)
            self.fail('Api mismatch not detected')
        except ApiMismatch:
            pass

    def test_match_call_with_unicode_and_non_ascii_chars(self):
        non_ascii  = u'España'
        self.spy.one_arg_method(non_ascii)

        assert_that(self.spy.one_arg_method, called_with(non_ascii))

#        pyDoubles:
#        assert_that_was_called(self.spy.one_arg_method).with_args(
#                                                        non_ascii)

#    def test_stub_methods_can_be_handled_separately(self):
#        when(self.spy.one_arg_method).with_args(1).then_return(1000)
#        when(self.spy.two_args_method).with_args(5, 5).then_return(2000)
#        handle1 = self.spy.one_arg_method
#        handle2 = self.spy.two_args_method
#        self.assertEquals(1000, handle1(1))
#        self.assertEquals(2000, handle2(5, 5))
#
#        assert_that_was_called(handle1).with_args(1)
#        assert_that_was_called(handle2).with_args(5, 5)

#    #SAME as VerifiedSpyTests.test_check_unexisting_method
#    def test_assert_was_called_with_method_not_in_the_api(self):
#        self.failUnlessRaises(ApiMismatch,
#            assert_that_was_called, self.spy.unexisting_method)

#    def test_do_not_call_callable_object_if_wasnt_generated_by_the_framework(self):
#        class CallableObj():
#            just_testing = True
#
#            def __call__(self, *args, **kwargs):
#                raise Exception('should not happen')
#
#        obj = CallableObj()
#        when(self.spy.one_arg_method).then_return(obj)
#
#        self.assertEquals(obj, self.spy.one_arg_method(1),
#                       "Wrong returned object")
