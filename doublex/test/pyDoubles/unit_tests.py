# -*- coding: utf-8 -*-

"""
Authors:
    Carlos Ble (www.carlosble.com)
    Ruben Bernardez (www.rubenbp.com)
    www.iExpertos.com
License: Apache 2 (http://www.apache.org/licenses/LICENSE-2.0.html)
Project home: https://bitbucket.org/carlosble/pydoubles
"""

import unittest
import re
from nose.tools import nottest

from doublex.pyDoubles import *


class SomeException(Exception):
    pass


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


class ProxySpyTests(unittest.TestCase):
    def setUp(self):
        self.spy = proxy_spy(Collaborator())

    def test_assert_was_called(self):
        self.spy.hello()

        assert_that_was_called(self.spy.hello)

    def test_other_way_of_assert_called(self):
        self.spy.hello()

        assert_that_method(self.spy.hello).was_called()

    def test_assert_was_called_on_any_method(self):
        self.spy.something()

        assert_that_was_called(self.spy.something)

    def test_assert_needs_always_a_method_from_a_double(self):
        self.failUnlessRaises(WrongApiUsage,
             assert_that_was_called, self.spy)

    def test_assert_needs_always_a_method_from_a_double_not_the_original(self):
        self.failUnlessRaises(WrongApiUsage,
             assert_that_was_called, Collaborator().hello)

    def test_one_method_called_other_wasnt(self):
        self.spy.something()

        self.failUnlessRaises(UnexpectedBehavior,
             assert_that_was_called, self.spy.hello)

    def test_two_methods_called_assert_on_the_first(self):
        self.spy.hello()
        self.spy.something()

        assert_that_was_called(self.spy.hello)

# pyDobules internal API specific
#    def test_get_method_name(self):
#        name = _Introspector_().method_name(self.spy.hello)
#
#        self.assertEquals("hello", name)

    def test_call_original_method(self):
        self.assertEquals("ok", self.spy.something())

# pyDobules internal API specific
#    def test_get_instance_from_method(self):
#        spy_found = _Introspector_().double_instance_from_method(self.spy.hello)
#
#        self.assertEquals(self.spy, spy_found)

    def test_assert_was_called_when_wasnt(self):
        self.failUnlessRaises(UnexpectedBehavior,
             assert_that_was_called, self.spy.hello)

    def test_was_called_with_same_parameters(self):
        self.spy.one_arg_method(1)

        assert_that_was_called(self.spy.one_arg_method).with_args(1)

    def test_was_called_with_same_parameters_in_variables(self):
        arg1 = 1
        self.spy.one_arg_method(arg1)

        assert_that_was_called(self.spy.one_arg_method).with_args(1)

    def test_was_called_with_same_parameters_when_not(self):
        self.spy.one_arg_method(1)
        args_checker = assert_that_was_called(self.spy.one_arg_method)

        self.failUnlessRaises(ArgsDontMatch,
            args_checker.with_args, 2)

    def test_was_called_with_same_params_but_no_params_accepted(self):
        self.spy.hello()
        args_checker = assert_that_was_called(self.spy.hello)

        self.failUnlessRaises(ArgsDontMatch,
            args_checker.with_args, "something")

    def test_was_called_with_several_parameters(self):
        self.spy.two_args_method(1, 2)
        args_checker = assert_that_was_called(self.spy.two_args_method)

        args_checker.with_args(1, 2)

    def test_was_called_with_parameters_not_matching(self):
        self.spy.one_arg_method(1)
        args_checker = assert_that_was_called(self.spy.one_arg_method)

        self.failUnlessRaises(ArgsDontMatch,
            args_checker.with_args, "2")

    def test_was_called_with_keyed_args_not_matching(self):
        self.spy.kwarg_method(key_param="foo")
        args_checker = assert_that_was_called(self.spy.kwarg_method)

        self.failUnlessRaises(ArgsDontMatch,
            args_checker.with_args, key_param="bar")

    def test_was_called_with_keyed_args_matching(self):
        self.spy.kwarg_method(key_param="foo")
        assert_that_was_called(self.spy.kwarg_method).with_args(
                                    key_param="foo")

    def test_recorded_call_params_are_displayed(self):
        self.spy.kwarg_method(key_param="foo")
        try:
            assert_that_was_called(self.spy.kwarg_method
                                   ).with_args("bar")
        except ArgsDontMatch, e:
            self.assertTrue(str(e).find("foo") != -1, str(e))

    def test_stub_out_method(self):
        when(self.spy.one_arg_method).then_return(3)

        self.assertEquals(3, self.spy.one_arg_method(5))

    def test_stub_method_was_called(self):
        when(self.spy.one_arg_method).then_return(3)
        self.spy.one_arg_method(5)
        assert_that_was_called(self.spy.one_arg_method).with_args(5)

    def test_stub_out_method_returning_a_list(self):
        when(self.spy.one_arg_method).then_return([1, 2, 3])

        self.assertEquals([1, 2, 3], self.spy.one_arg_method(5))

    def test_stub_method_returning_list_was_called(self):
        when(self.spy.one_arg_method).then_return([1, 2, 3])
        self.spy.one_arg_method(5)
        assert_that_was_called(self.spy.one_arg_method).with_args(5)

    def test_stub_out_method_with_args(self):
        when(self.spy.one_arg_method).with_args(2).then_return(3)

        self.assertEquals(3, self.spy.one_arg_method(2))

    def test_stub_method_with_args_was_called(self):
        when(self.spy.one_arg_method).with_args(2).then_return(3)

        self.spy.one_arg_method(2)

        assert_that_was_called(self.spy.one_arg_method).with_args(2)

    def test_stub_out_method_with_args_calls_actual(self):
        when(self.spy.one_arg_method).with_args(2).then_return(3)

        self.assertEquals(4, self.spy.one_arg_method(4))

        assert_that_was_called(self.spy.one_arg_method).with_args(4)

    def test_stub_out_method_with_several_inputs(self):
        when(self.spy.one_arg_method).with_args(2).then_return(3)
        when(self.spy.one_arg_method).with_args(3).then_return(4)

        self.assertEquals(3, self.spy.one_arg_method(2))
        self.assertEquals(4, self.spy.one_arg_method(3))

    def test_recorded_calls_work_on_several_stubs(self):
        when(self.spy.one_arg_method).with_args(2).then_return(3)
        when(self.spy.one_arg_method).with_args(3).then_return(4)

        self.spy.one_arg_method(2)
        self.spy.one_arg_method(3)
        assert_that_was_called(self.spy.one_arg_method).with_args(2)
        assert_that_was_called(self.spy.one_arg_method).with_args(3)

    def test_matching_stub_definition_is_used(self):
        when(self.spy.one_arg_method).then_return(1000)
        when(self.spy.one_arg_method).with_args(2).then_return(3)

        self.assertEquals(3, self.spy.one_arg_method(2))
        self.assertEquals(1000, self.spy.one_arg_method(8))

    def test_stub_with_kwargs(self):
        when(self.spy.kwarg_method).with_args(key_param=2
                                            ).then_return(3)

        self.assertEquals(3, self.spy.kwarg_method(key_param=2))
        self.assertEquals(6, self.spy.kwarg_method(key_param=6))

    def test_stub_raising_exception(self):
        when(self.spy.hello).then_raise(SomeException())
        try:
            self.spy.hello()
            self.fail("not raised")
        except SomeException:
            pass

    def test_stub_returning_what_receives(self):
        when(self.spy.method_one).then_return_input()

        self.assertEquals(20, self.spy.method_one(20))

    def test_stub_returning_what_receives_when_no_params(self):
        when(self.spy.hello).then_return_input()

        self.failUnlessRaises(ApiMismatch, self.spy.hello)

    def test_be_able_to_return_objects(self):
        when(self.spy.one_arg_method).then_return(Collaborator())

        collaborator = self.spy.one_arg_method(1)

        self.assertEquals(1, collaborator.one_arg_method(1))

    def test_any_arg_matcher(self):
        when(self.spy.two_args_method).with_args(1, ANY_ARG).then_return(1000)

        self.assertEquals(1000, self.spy.two_args_method(1, 2))
        self.assertEquals(1000, self.spy.two_args_method(1, 5))

## TODO: implement this:
## pyDoubles did not support this
##    def test_any_arg_matcher_with_kwargs(self):
##        when(self.spy.kwarg_method).with_args(key_param=ANY_ARG).then_return(1000)
##
##        self.assertEquals(1000, self.spy.kwarg_method(key_param=2))

    def test_any_arg_matcher_was_called(self):
        when(self.spy.two_args_method).with_args(1, 2).then_return(1000)

        self.spy.two_args_method(1, 2)

        assert_that_was_called(self.spy.two_args_method
                               ).with_args(1, ANY_ARG)

    def test_stub_works_with_alias_method(self):
        when(self.spy.one_arg_method).with_args(1).then_return(1000)

        self.spy.alias_method(1)
        assert_that_was_called(self.spy.one_arg_method
                               ).with_args(1)

    def test_was_never_called(self):
        assert_that_method(self.spy.one_arg_method).was_never_called()

    def test_was_never_called_is_false(self):
        self.spy.one_arg_method(1)
        try:
            assert_that_method(self.spy.one_arg_method).was_never_called()
            self.fail("it was called indeed!")
        except UnexpectedBehavior:
            pass

    def test_expect_several_times(self):
        self.spy.one_arg_method(1)

        try:
            assert_that_method(self.spy.one_arg_method).was_called().times(2)
            self.fail("Should have been called 2 times")
        except UnexpectedBehavior:
            pass

    def test_fail_incorrect_times_msg_is_human_readable(self):
        self.spy.one_arg_method(1)

        try:
            assert_that_method(self.spy.one_arg_method).was_called().times(5)
            self.fail("Should have been called 2 times")
        except UnexpectedBehavior, e:
            for arg in e.args:
                if re.search("5", arg) and re.search("one_arg_method", arg):
                    return
            self.fail("No enough readable exception message")

    def test_expect_several_times_matches_exactly(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that_method(self.spy.one_arg_method).was_called().times(2)

    def test_expect_several_times_with_args_definition(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that_method(self.spy.one_arg_method).was_called().with_args(1).times(2)

    def test_expect_several_times_with_incorrect_args(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)

        try:
            assert_that_method(self.spy.one_arg_method).was_called().with_args(2).times(2)
            self.fail("Must have 1 as an argument")
        except ArgsDontMatch:
            pass

    def test_args_match_but_not_number_of_times(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(2)
        try:
            assert_that_method(self.spy.one_arg_method
                ).was_called().with_args(1).times(2)
            self.fail("Wrong assertion")
        except UnexpectedBehavior:
            pass

# pyDobules internal API specific
#class MethodPoolTests(unittest.TestCase):
#
#    def setUp(self):
#        self.pool = _MethodPool_()
#        self.method_name = "some_method"
#        self.pool.add_invocation(
#            CallDescription(self.method_name, (1, 2)))
#
#    def test_call_args_match(self):
#        self.assertTrue(
#            self.pool.matching_invocations_by_args(
#                CallDescription(self.method_name, (1, 2), {})))
#
#    def test_call_args_match_with_any(self):
#        self.assertTrue(
#            self.pool.matching_invocations_by_args(
#                CallDescription(self.method_name, (1, ANY_ARG), {})))


class SpyTests(unittest.TestCase):
    def setUp(self):
        self.spy = spy(Collaborator())

    def test_override_original_method(self):
        self.assertTrue(self.spy.hello() is None)

    def test_override_original_method_and_is_called(self):
        self.spy.hello()
        assert_that_was_called(self.spy.hello)

    def test_spy_can_work_from_empty_object(self):
        self.spy = empty_spy()
        self.assertTrue(self.spy.hello() is None)

    def test_spy_without_args_is_empty_spy(self):
        self.spy = spy()
        self.assertTrue(self.spy.hello() is None)

    def test_spy_can_work_from_empty_and_is_called(self):
        self.spy.hello()
        assert_that_was_called(self.spy.hello)

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

        assert_that_was_called(self.spy.one_arg_method).with_args(
                                                        non_ascii)

    def test_stub_methods_can_be_handled_separately(self):
        when(self.spy.one_arg_method).with_args(1).then_return(1000)
        when(self.spy.two_args_method).with_args(5, 5).then_return(2000)
        handle1 = self.spy.one_arg_method
        handle2 = self.spy.two_args_method
        self.assertEquals(1000, handle1(1))
        self.assertEquals(2000, handle2(5, 5))

        assert_that_was_called(handle1).with_args(1)
        assert_that_was_called(handle2).with_args(5, 5)

    def test_assert_was_called_with_method_not_in_the_api(self):
#:pyDoubles
#        self.failUnlessRaises(ApiMismatch,
#            assert_that_was_called, self.spy.unexisting_method)

        try:
            self.spy.unexisting_method()
            self.fail("Exception should be raised")
        except AttributeError:
            pass

    def test_do_not_call_callable_object_if_wasnt_generated_by_the_framework(self):
        class CallableObj():
            just_testing = True

            def __call__(self, *args, **kwargs):
                raise Exception('should not happen')

        obj = CallableObj()
        when(self.spy.one_arg_method).then_return(obj)

        self.assertEquals(obj, self.spy.one_arg_method(1),
                        "Wrong returned object")

    # bitbucket Issue #5
    def test_fail_missing_fluent_method(self):
        try:
            self.spy.one_arg_method(1)
            assert_that_was_called(self.spy.one_arg_method).with_params(2)  # should be with_args
            self.fail("TypeError should be raised")

        except AttributeError, e:
            expected = "'assert_that_method' object has no attribute 'with_params'"
            hamcrest.assert_that(str(e), hamcrest.contains_string(expected))


class MockTests(unittest.TestCase):

    def setUp(self):
        self.mock = mock(Collaborator())

    def test_fail_on_unexpected_call(self):
        try:
            self.mock.hello()
            self.fail('UnexpectedBehavior should be raised')
        except UnexpectedBehavior:
            pass

    def test_fail_on_unexpected_call_msg_is_human_readable(self):
        try:
            self.mock.hello()
        except UnexpectedBehavior, e:
            for arg in e.args:
                if re.search("No one", arg):
                    return
            self.fail("No enough readable exception message")

    def test_define_expectation_and_call_method(self):
        expect_call(self.mock.hello)
        self.assertTrue(self.mock.hello() is None)

    def test_define_several_expectatiosn(self):
        expect_call(self.mock.hello)
        expect_call(self.mock.one_arg_method)

        self.assertTrue(self.mock.hello() is None)
        self.assertTrue(self.mock.one_arg_method(1) is None)

    def test_define_expectation_args(self):
        expect_call(self.mock.one_arg_method).with_args(1)
        self.assertTrue(self.mock.one_arg_method(1) is None)

    def test_define_expectation_args_and_fail(self):
        expect_call(self.mock.one_arg_method).with_args(1)
        try:
            self.mock.one_arg_method(2)
            self.fail('Unexpected call')
        except UnexpectedBehavior:
            pass

    def test_several_expectations_with_args(self):
        expect_call(self.mock.one_arg_method).with_args(1)
        expect_call(self.mock.two_args_method).with_args(2, 3)

        self.assertTrue(self.mock.one_arg_method(1) is None)
        self.assertTrue(self.mock.two_args_method(2, 3) is None)

    def test_expect_call_returning_value(self):
        expect_call(self.mock.one_arg_method).with_args(1).returning(1000)

        self.assertEquals(1000, self.mock.one_arg_method(1))

    def test_assert_expectations_are_satisfied(self):
        expect_call(self.mock.hello)
        try:
            self.mock.assert_that_is_satisfied()
            self.fail('Not satisfied!')
        except UnexpectedBehavior:
            pass

    def test_assert_expectations_alternative(self):
        expect_call(self.mock.hello)
        try:
            self.mock.assert_expectations()
            self.fail('Not satisfied')
        except UnexpectedBehavior:
            pass

    def test_assert_satisfied_when_it_really_is(self):
        expect_call(self.mock.hello)
        self.mock.hello()
        self.mock.assert_that_is_satisfied()

    def test_number_of_calls_matter(self):
        expect_call(self.mock.hello)
        self.mock.hello()
        self.mock.hello()
        self.failUnlessRaises(UnexpectedBehavior,
                        self.mock.assert_that_is_satisfied)

    def test_using_when_or_expect_call_without_double(self):
        self.failUnlessRaises(WrongApiUsage,
                        expect_call, Collaborator())

    def test_expectations_on_synonyms(self):
        expect_call(self.mock.one_arg_method)

        self.mock.alias_method(1)

        self.mock.assert_that_is_satisfied()

    def test_several_expectations_with_different_args(self):
        expect_call(self.mock.one_arg_method).with_args(1)
        expect_call(self.mock.one_arg_method).with_args(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        self.failUnlessRaises(UnexpectedBehavior,
            self.mock.assert_that_is_satisfied)

    def test_expect_several_times(self):
        expect_call(self.mock.one_arg_method).with_args(1).times(2)

        self.mock.one_arg_method(1)

        self.failUnlessRaises(UnexpectedBehavior,
            self.mock.assert_that_is_satisfied)

    def test_expect_several_times_matches_exactly(self):
        expect_call(self.mock.one_arg_method).with_args(1).times(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        self.mock.assert_that_is_satisfied()

    def test_expect_several_times_without_args_definition(self):
        expect_call(self.mock.one_arg_method).times(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        self.mock.assert_that_is_satisfied()

    def test_defend_agains_less_than_2_times(self):
        try:
            expect_call(self.mock.one_arg_method).times(1)
            self.fail('times cant be less than 2')
        except WrongApiUsage:
            pass

    def test_times_and_return_value(self):
        expect_call(self.mock.one_arg_method).returning(1000).times(2)

        self.assertEquals(1000, self.mock.one_arg_method(1))
        self.assertEquals(1000, self.mock.one_arg_method(1))

        self.mock.assert_that_is_satisfied()

    def test_times_and_return_value_and_input_args(self):
        expect_call(self.mock.one_arg_method).with_args(10).returning(1000).times(2)

        self.assertEquals(1000, self.mock.one_arg_method(10))
        self.assertEquals(1000, self.mock.one_arg_method(10))

        self.mock.assert_that_is_satisfied()


class MockFromEmptyObjectTests(unittest.TestCase):
    def setUp(self):
        self.mock = empty_mock()

    def test_mock_can_work_from_empty_object(self):
        expect_call(self.mock.hello)

        self.mock.hello()

        self.mock.assert_that_is_satisfied()

    def test_mock_without_args_is_empty_mock(self):
        self.mock = mock()
        expect_call(self.mock.hello)

        self.mock.hello()

        self.mock.assert_that_is_satisfied()

    def test_several_expectations_in_empty_mock(self):
        expect_call(self.mock.hello)
        expect_call(self.mock.one_arg_method).with_args(1)

        self.mock.hello()
        self.mock.one_arg_method(1)

        self.mock.assert_that_is_satisfied()

    def test_several_expectations_with_args_in_empty_mock(self):
        expect_call(self.mock.one_arg_method).with_args(1)
        expect_call(self.mock.one_arg_method).with_args(2)

        self.assertTrue(self.mock.one_arg_method(1) is None)
        self.assertTrue(self.mock.one_arg_method(2) is None)

        self.mock.assert_that_is_satisfied()


class StubMethodsTests(unittest.TestCase):

    def setUp(self):
        self.collaborator = Collaborator()

    def test_method_returning_value(self):
        self.collaborator.hello = method_returning("bye")

        self.assertEquals("bye", self.collaborator.hello())

    def test_method_args_returning_value(self):
        self.collaborator.one_arg_method = method_returning("bye")

        self.assertEquals("bye", self.collaborator.one_arg_method(1))

    def test_method_raising_exception(self):
        self.collaborator.hello = method_raising(SomeException())
        try:
            self.collaborator.hello()
            self.fail("exception not raised")
        except SomeException:
            pass


class MatchersTests(unittest.TestCase):

    def setUp(self):
        self.spy = spy(Collaborator())

    def test_str_cotaining_with_exact_match(self):
        when(self.spy.one_arg_method).with_args(
                    str_containing("abc")).then_return(1000)

        self.assertEquals(1000, self.spy.one_arg_method("abc"))

    def test_str_containing_with_substr(self):
        when(self.spy.one_arg_method).with_args(
                    str_containing("abc")).then_return(1000)

        self.assertEquals(1000, self.spy.one_arg_method("XabcX"))

    def test_str_containing_with_substr_unicode(self):
        when(self.spy.one_arg_method).with_args(
                    str_containing("abc")).then_return(1000)

        self.assertEquals(1000, self.spy.one_arg_method(u"XabcñX"))

    def test_str_containing_but_matcher_not_used(self):
        when(self.spy.one_arg_method).with_args(
                        "abc").then_return(1000)

        self.assertNotEquals(1000, self.spy.one_arg_method("XabcX"))

    def test_was_called_and_substr_matcher(self):
        self.spy.one_arg_method("XabcX")

        assert_that_was_called(self.spy.one_arg_method).with_args(
                                    str_containing("abc"))

    def test_str_not_containing(self):
        when(self.spy.one_arg_method).with_args(
                        str_not_containing("abc")).then_return(1000)

        self.assertNotEquals(1000, self.spy.one_arg_method("abc"))

    def test_str_not_containing_stubs_anything_else(self):
        when(self.spy.one_arg_method).with_args(
                        str_not_containing("abc")).then_return(1000)

        self.assertEquals(1000, self.spy.one_arg_method("xxx"))

    def test_str_not_containing_was_called(self):
        self.spy.one_arg_method("abc")
        assert_that_was_called(self.spy.one_arg_method).with_args(
                                str_not_containing("xxx"))

    def test_several_matchers(self):
        when(self.spy.two_args_method).with_args(
                        str_containing("abc"),
                        str_containing("xxx")).then_return(1000)

        self.assertNotEquals(1000,
                    self.spy.two_args_method("abc", "yyy"))

    def test_str_length_matcher(self):
        when(self.spy.one_arg_method).with_args(
                        str_length(5)).then_return(1000)

        self.assertEquals(1000,
                    self.spy.one_arg_method("abcde"))

    def test_matchers_when_passed_arg_is_none(self):
        when(self.spy.one_arg_method).with_args(
                        str_length(5)).then_return(1000)
        self.assertTrue(self.spy.one_arg_method(None) is None)

    def test_compare_objects_is_not_possible_without_eq_operator(self):
        class SomeObject():
            field1 = field2 = None

        obj = SomeObject()
        obj2 = SomeObject()
        self.spy.one_arg_method(obj)

        try:
            assert_that_method(self.spy.one_arg_method).was_called().with_args(obj2)
            self.fail('they should not match')
        except ArgsDontMatch:
            pass

    def test_if_doesnt_match_message_is_human_redable(self):
        self.spy.one_arg_method("XabcX")

        try:
            assert_that_was_called(self.spy.one_arg_method).with_args(
                                   str_containing("xxx"))

        except ArgsDontMatch, e:
            self.assertTrue("xxx" in str(e.args), str(e.args))
            self.assertTrue("string containing" in str(e.args))

    def test_obj_with_field_matcher(self):
        obj = Collaborator()
        obj.id = 20
        self.spy.one_arg_method(obj)
        assert_that_method(self.spy.one_arg_method
            ).was_called().with_args(obj_with_fields({'id': 20}))

    def test_obj_with_several_fields_matcher(self):
        obj = Collaborator()
        obj.id = 21
        self.spy.one_arg_method(obj)
        try:
            assert_that_method(
                self.spy.one_arg_method).was_called().with_args(
                obj_with_fields({
                            'id': 20,
                            'test_field': 'OK'}))
            self.fail('Wrong assertion, id field is different')
        except ArgsDontMatch:
            pass

    def test_obj_with_field_defends_agains_wrong_usage(self):
        self.spy.one_arg_method(Collaborator())
        try:
            assert_that_method(
                self.spy.one_arg_method).was_called().with_args(
                obj_with_fields('id = 20'))
            self.fail('Wrong assertion, argument should be a dictionary')
        except WrongApiUsage:
            pass


# Create hamcrest matchers instead
#class CustomMatchersTest(unittest.TestCase):
#
#    def setUp(self):
#        self.spy = spy(Collaborator())
#
#    def test_use_custom_matcher(self):
#        class CustomMatcher(PyDoublesMatcher):
#            matcher_name = "test matcher"
#
#            def __init__(self, arg):
#                self.defined_arg = arg
#
#            def matches(self, item):
#                return True
#
#        when(self.spy.one_arg_method).with_args(
#            CustomMatcher('zzz')).then_return(1000)
#        self.assertEquals(1000, self.spy.one_arg_method('xx'))
#
#    def test_custom_matcher_do_not_follow_convention(self):
#        class CustomMatcher(PyDoublesMatcher):
#            def matches(self, item):
#                return False
#
#        self.spy.one_arg_method(1)
#        try:
#            assert_that_was_called(self.spy.one_arg_method).with_args(
#                                   CustomMatcher())
#            self.fail('args dont match!')
#        except ArgsDontMatch:
#            pass


if __name__ == "__main__":
    print "Use nosetest to run this tests: nosetest unit.py"
