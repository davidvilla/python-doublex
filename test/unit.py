# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase

from hamcrest import assert_that, is_not, is_

from doublex import Spy, ProxySpy
from doublex import called, called_with, ANY_ARG
from doublex import ApiMismatch, WrongApiUsage
import doublex.tools as tools


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
        self.spy = Spy(Actor)


class ProxySpyTest(TestCase):
    def test_must_give_argument(self):
        self.failUnlessRaises(TypeError, ProxySpy)

    def test_given_argument_can_not_be_oldstyle_class(self):
        self.failUnlessRaises(AssertionError,
                              ProxySpy, Collaborator)

    def test_given_argument_can_not_be_newstyle_class(self):
        self.failUnlessRaises(AssertionError,
                              ProxySpy, Actor)


class Actor(object):
    pass



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


class pyDoubles__ProxySpyTests(TestCase):
    def setUp(self):
        self.spy = ProxySpy(Collaborator())

    #SAME as pyDoublesSpyTests.test_override_original_method_and_is_called
    def test_assert_was_called(self):
        self.spy.hello()

        assert_that(self.spy.hello, called())

    def test_assert_was_called_on_any_method(self):
        self.spy.something()

        assert_that(self.spy.something, called())

    def test_assert_needs_always_a_method_from_a_double(self):
        self.failUnlessRaises(
            WrongApiUsage,
            assert_that, self.spy, called())

    def test_assert_needs_always_a_method_from_a_double_not_the_original(self):
        self.failUnlessRaises(
            WrongApiUsage,
            assert_that, Collaborator().hello, called())

    def test_one_method_called_other_wasnt(self):
        self.spy.something()

        self.failUnlessRaises(
            AssertionError,
            assert_that, self.spy.hello, called())

    def test_two_methods_called_assert_on_the_first(self):
        self.spy.hello()
        self.spy.something()

        assert_that(self.spy.hello, called())

#    # This is testing internal API! Not applicable
#    def test_get_method_name(self):
#        name = _Introspector_().method_name(self.spy.hello)
#
#        self.assertEquals("hello", name)

    def test_call_original_method(self):
        self.assertEquals("ok", self.spy.something())

#    # This is testing internal API! Not applicable
#    def test_get_instance_from_method(self):
#        spy_found = _Introspector_().double_instance_from_method(self.spy.hello)
#
#        self.assertEquals(self.spy, spy_found)

    def test_assert_was_called_when_wasnt(self):
        self.failUnlessRaises(
            AssertionError,
            assert_that, self.spy.hello, called())

    def test_was_called_with_same_parameters(self):
        self.spy.one_arg_method(1)

        assert_that(self.spy.one_arg_method, called_with(1))

    # this is exactly the same that previous! :-S
    def test_was_called_with_same_parameters_in_variables(self):
        arg1 = 1
        self.spy.one_arg_method(arg1)

        assert_that(self.spy.one_arg_method, called_with(1))

    def test_was_called_with_same_parameters_when_not(self):
        self.spy.one_arg_method(1)
        args_checker = called_with(2)

        assert_that(not args_checker.matches(self.spy.one_arg_method))

    def test_was_called_with_same_params_but_no_params_accepted(self):
        self.spy.hello()
        args_checker = called_with("something")

        assert_that(not args_checker.matches(self.spy.hello))

    def test_was_called_with_several_parameters(self):
        self.spy.two_args_method(1, 2)
        args_checker = called_with(1, 2)

        assert_that(args_checker.matches(self.spy.two_args_method))

    #SAME as test_was_called_with_same_parameters_when_not
    def test_was_called_with_parameters_not_matching(self):
        self.spy.one_arg_method(1)
        args_checker = called_with("2")

        assert_that(not args_checker.matches(self.spy.one_arg_method))

    def test_was_called_with_keyed_args_not_matching(self):
        self.spy.kwarg_method(key_param="foo")
        args_checker = called_with(key_param="bar")

        assert_that(not args_checker.matches(self.spy.kwarg_method))

    def test_was_called_with_keyed_args_matching(self):
        self.spy.kwarg_method(key_param="foo")
        assert_that(self.spy.kwarg_method, called_with(key_param="foo"))

    def test_recorded_call_params_are_displayed(self):
        self.spy.kwarg_method(key_param="foo")
        try:
            assert_that(self.spy.kwarg_method, called_with("bar"))
        except AssertionError, e:
#            print e
            self.assertIn("foo", str(e))

#    def test_stub_out_method(self):
#        when(self.spy.one_arg_method).then_return(3)
#
#        self.assertEquals(3, self.spy.one_arg_method(5))
#
#    def test_stub_method_was_called(self):
#        when(self.spy.one_arg_method).then_return(3)
#        self.spy.one_arg_method(5)
#        assert_that_was_called(self.spy.one_arg_method).with_args(5)
#
#    def test_stub_out_method_returning_a_list(self):
#        when(self.spy.one_arg_method).then_return([1, 2, 3])
#
#        self.assertEquals([1, 2, 3], self.spy.one_arg_method(5))
#
#    def test_stub_method_returning_list_was_called(self):
#        when(self.spy.one_arg_method).then_return([1, 2, 3])
#        self.spy.one_arg_method(5)
#        assert_that_was_called(self.spy.one_arg_method).with_args(5)
#
#    def test_stub_out_method_with_args(self):
#        when(self.spy.one_arg_method).with_args(2).then_return(3)
#
#        self.assertEquals(3, self.spy.one_arg_method(2))
#
#    def test_stub_method_with_args_was_called(self):
#        when(self.spy.one_arg_method).with_args(2).then_return(3)
#        self.spy.one_arg_method(2)
#
#        assert_that_was_called(self.spy.one_arg_method).with_args(2)
#
#    def test_stub_out_method_with_args_calls_actual(self):
#        when(self.spy.one_arg_method).with_args(2).then_return(3)
#
#        self.assertEquals(4, self.spy.one_arg_method(4))
#
#        assert_that_was_called(self.spy.one_arg_method).with_args(4)
#
#    def test_stub_out_method_with_several_inputs(self):
#        when(self.spy.one_arg_method).with_args(2).then_return(3)
#        when(self.spy.one_arg_method).with_args(3).then_return(4)
#
#        self.assertEquals(3, self.spy.one_arg_method(2))
#        self.assertEquals(4, self.spy.one_arg_method(3))
#
#    def test_recorded_calls_work_on_several_stubs(self):
#        when(self.spy.one_arg_method).with_args(2).then_return(3)
#        when(self.spy.one_arg_method).with_args(3).then_return(4)
#
#        self.spy.one_arg_method(2)
#        self.spy.one_arg_method(3)
#        assert_that_was_called(self.spy.one_arg_method).with_args(2)
#        assert_that_was_called(self.spy.one_arg_method).with_args(3)
#
#    def test_matching_stub_definition_is_used(self):
#        when(self.spy.one_arg_method).then_return(1000)
#        when(self.spy.one_arg_method).with_args(2).then_return(3)
#        self.assertEquals(3, self.spy.one_arg_method(2))
#        self.assertEquals(1000, self.spy.one_arg_method(8))
#
#    def test_stub_with_kwargs(self):
#        when(self.spy.kwarg_method).with_args(key_param=2
#                                            ).then_return(3)
#
#        self.assertEquals(3, self.spy.kwarg_method(key_param=2))
#        self.assertEquals(6, self.spy.kwarg_method(key_param=6))
#
#    def test_stub_raising_exception(self):
#        when(self.spy.hello).then_raise(SomeException())
#        try:
#            self.spy.hello()
#            self.fail("not raised")
#        except SomeException:
#            pass
#
#    def test_stub_returning_what_receives(self):
#        when(self.spy.method_one).then_return_input()
#
#        self.assertEquals(20, self.spy.method_one(20))
#
#    def test_stub_returning_what_receives_when_no_params(self):
#        when(self.spy.hello).then_return_input()
#
#        self.failUnlessRaises(ApiMismatch, self.spy.hello)
#
#    def test_be_able_to_return_objects(self):
#        when(self.spy.one_arg_method).then_return(Collaborator())
#
#        collaborator = self.spy.one_arg_method(1)
#
#        self.assertEquals(1, collaborator.one_arg_method(1))
#
#    def test_any_arg_matcher(self):
#        when(self.spy.two_args_method).with_args(1, ANY_ARG).then_return(1000)
#
#        self.assertEquals(1000, self.spy.two_args_method(1, 2))
#        self.assertEquals(1000, self.spy.two_args_method(1, 5))
#
## TODO: implement this:
##    def test_any_arg_matcher_with_kwargs(self):
##        when(self.spy.kwarg_method).with_args(key_param=ANY_ARG).then_return(1000)
##
##        self.assertEquals(1000, self.spy.kwarg_method(key_param=2))
#
#    def test_any_arg_matcher_was_called(self):
#        when(self.spy.two_args_method).with_args(1, 2).then_return(1000)
#
#        self.spy.two_args_method(1, 2)
#
#        assert_that_was_called(self.spy.two_args_method
#                               ).with_args(1, ANY_ARG)
#
#    def test_stub_works_with_alias_method(self):
#        when(self.spy.one_arg_method).with_args(1).then_return(1000)
#
#        self.spy.alias_method(1)
#        assert_that_was_called(self.spy.one_arg_method
#                               ).with_args(1)

    def test_was_never_called(self):
        assert_that(self.spy.one_arg_method, is_not(called()))

    def test_was_never_called_is_false(self):
        self.spy.one_arg_method(1)
        try:
            assert_that(self.spy.one_arg_method, is_not(called()))
            self.fail("it was called indeed!")
        except AssertionError:
            pass

    def test_expect_several_times(self):
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called().times(2))
            self.fail("Should have been called 2 times")
        except AssertionError:
            pass

    def test_fail_incorrect_times_msg_is_human_readable(self):
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called().times(5))
            self.fail("Should have been called 5 times")
        except AssertionError, e:
            self.assertIn("5", str(e))
            self.assertIn("one_arg_method", str(e))

    def test_expect_several_times_matches_exactly(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that(self.spy.one_arg_method, called().times(2))

    def test_expect_several_times_with_args_definition(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that(self.spy.one_arg_method, called_with(1).times(2))

    def test_expect_several_times_with_incorrect_args(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called_with(2).times(2))
            self.fail("Must have 1 as an argument")
        except AssertionError:
            pass

    def test_args_match_but_not_number_of_times(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(2)
        try:
            assert_that(self.spy.one_arg_method,
                        called_with(1).times(2))
            self.fail("Wrong assertion")
        except AssertionError:
            pass


class pyDoubles__SpyTests(TestCase):
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
