# -*- coding:utf-8; tab-width:4; mode:python -*-


from unittest import TestCase

from hamcrest import is_not, all_of, contains_string, has_length
from hamcrest.library.object.hasproperty import *
from doublex import *

from unit_tests import Collaborator


class SomeException(Exception):
    pass


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

        assert_that(self.spy.one_arg_method, called().with_args(1))

    # this is exactly the same that previous! :-S
    def test_was_called_with_same_parameters_in_variables(self):
        arg1 = 1
        self.spy.one_arg_method(arg1)

        assert_that(self.spy.one_arg_method, called().with_args(1))

    def test_was_called_with_same_parameters_when_not(self):
        self.spy.one_arg_method(1)
        args_checker = called().with_args(2)

        assert_that(not args_checker.matches(self.spy.one_arg_method))

    def test_was_called_with_same_params_but_no_params_accepted(self):
        self.spy.hello()
        args_checker = called().with_args("something")

        assert_that(not args_checker.matches(self.spy.hello))

    def test_was_called_with_several_parameters(self):
        self.spy.two_args_method(1, 2)
        args_checker = called().with_args(1, 2)

        assert_that(args_checker.matches(self.spy.two_args_method))

    #SAME as test_was_called_with_same_parameters_when_not
    def test_was_called_with_parameters_not_matching(self):
        self.spy.one_arg_method(1)
        args_checker = called().with_args("2")

        assert_that(not args_checker.matches(self.spy.one_arg_method))

    def test_was_called_with_keyed_args_not_matching(self):
        self.spy.kwarg_method(key_param="foo")
        args_checker = called().with_args(key_param="bar")

        assert_that(not args_checker.matches(self.spy.kwarg_method))

    def test_was_called_with_keyed_args_matching(self):
        self.spy.kwarg_method(key_param="foo")
        assert_that(self.spy.kwarg_method, called().with_args(key_param="foo"))

    def test_recorded_call_params_are_displayed(self):
        self.spy.kwarg_method(key_param="foo")
        try:
            assert_that(self.spy.kwarg_method, called().with_args("bar"))
        except AssertionError, e:
            assert_that(str(e), contains_string("foo"))

    def test_stub_out_method(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(3)

        self.assertEquals(3, self.spy.one_arg_method(5))

    def test_stub_method_was_called(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(3)

        self.spy.one_arg_method(5)
        assert_that(self.spy.one_arg_method, called().with_args(5))

    def test_stub_out_method_returning_a_list(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns([1, 2, 3])

        assert_that(self.spy.one_arg_method(5), is_([1, 2, 3]))

    def test_stub_method_returning_list_was_called(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns([1, 2, 3])

        self.spy.one_arg_method(5)

        assert_that(self.spy.one_arg_method, called().with_args(5))

    def test_stub_out_method_with_args(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)

        assert_that(self.spy.one_arg_method(2), is_(3))

    def test_stub_method_with_args_was_called(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)

        self.spy.one_arg_method(2)

        assert_that(self.spy.one_arg_method, called().with_args(2))

    def test_stub_out_method_with_args_calls_actual(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)

        assert_that(self.spy.one_arg_method(4), is_(4))
        assert_that(self.spy.one_arg_method, called().with_args(4))

    def test_stub_out_method_with_several_inputs(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)
            self.spy.one_arg_method(3).returns(4)

        assert_that(self.spy.one_arg_method(2), is_(3))
        assert_that(self.spy.one_arg_method(3), is_(4))

    def test_recorded_calls_work_on_several_stubs(self):
        with self.spy:
            self.spy.one_arg_method(2).returns(3)
            self.spy.one_arg_method(3).returns(4)

        self.spy.one_arg_method(2)
        self.spy.one_arg_method(3)
        assert_that(self.spy.one_arg_method, called().with_args(2))
        assert_that(self.spy.one_arg_method, called().with_args(3))

    def test_matching_stub_definition_is_used(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(1000)
            self.spy.one_arg_method(2).returns(3)

        assert_that(self.spy.one_arg_method(2), is_(3))
        assert_that(self.spy.one_arg_method(8), is_(1000))

    def test_stub_with_kwargs(self):
        with self.spy:
            self.spy.kwarg_method(key_param=2).returns(3)

        assert_that(self.spy.kwarg_method(key_param=2), is_(3))
        assert_that(self.spy.kwarg_method(key_param=6), is_(6))

    def test_stub_raising_exception(self):
        with self.spy:
            self.spy.hello().raises(SomeException)

        try:
            self.spy.hello()
            self.fail("not raised")
        except SomeException:
            pass

    def test_stub_returning_what_receives(self):
        with self.spy:
            self.spy.method_one(ANY_ARG).returns_input()

        assert_that(self.spy.method_one(20), is_(20))

    # Different that pyDoubles. exception raised at setup
    def test_stub_returning_what_receives_when_no_params(self):
        try:
            with self.spy:
                self.spy.hello().returns_input()

            self.fail("TypeError should be raised")
        except TypeError, e:
            assert_that(str(e),
                        contains_string("Collaborator.hello() has no input args"))

    def test_be_able_to_return_objects(self):
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(Collaborator())

        collaborator = self.spy.one_arg_method(1)

        assert_that(collaborator.one_arg_method(1), is_(1))

    def test_any_arg_matcher(self):
        with self.spy:
            self.spy.two_args_method(1, ANY_ARG).returns(1000)

        assert_that(self.spy.two_args_method(1, 2), is_(1000))
        assert_that(self.spy.two_args_method(1, 5), is_(1000))
        assert_that(self.spy.two_args_method(3, 5), is_not(1000))

    # Not supported by pyDoubles
    def test_any_arg_matcher_with_kwargs(self):
        with self.spy:
            self.spy.kwarg_method(key_param=anything()).returns(1000)

        self.assertEquals(1000, self.spy.kwarg_method(key_param=2))

    def test_any_arg_matcher_was_called(self):
        with self.spy:
            self.spy.two_args_method(1, 2).returns(1000)

        self.spy.two_args_method(1, 2)

        assert_that(self.spy.two_args_method, called().with_args(1, ANY_ARG))

    def test_stub_works_with_alias_method(self):
        with self.spy:
            self.spy.one_arg_method(1).returns(1000)

        self.spy.alias_method(1)
        assert_that(self.spy.one_arg_method, called().with_args(1))

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
            assert_that(str(e), contains_string("5"))
            assert_that(str(e), contains_string("one_arg_method"))

    def test_expect_several_times_matches_exactly(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that(self.spy.one_arg_method, called().times(2))

    def test_expect_several_times_with_args_definition(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)
        assert_that(self.spy.one_arg_method, called().with_args(1).times(2))

    def test_expect_several_times_with_incorrect_args(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(1)

        try:
            assert_that(self.spy.one_arg_method, called().with_args(2).times(2))
            self.fail("Must have 1 as an argument")
        except AssertionError:
            pass

    def test_args_match_but_not_number_of_times(self):
        self.spy.one_arg_method(1)
        self.spy.one_arg_method(2)
        try:
            assert_that(self.spy.one_arg_method,
                        called().with_args(1).times(2))
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
            self.fail('Expection should raise: Actual object does not accept parameters')
        except TypeError:
            pass

    def test_check_api_match_with_kwargs(self):
        self.assertTrue(self.spy.mixed_method(1, key_param=2) is None)

    def test_check_api_match_with_kwargs_not_used(self):
        self.assertTrue(self.spy.mixed_method(1) is None)

    def test_check_api_match_with_kwargs_not_matching(self):
        try:
            self.spy.mixed_method(1, 2, 3)
            self.fail('TypeError not detected!')
        except TypeError:
            pass

    def test_match_call_with_unicode_and_non_ascii_chars(self):
        non_ascii  = u'España'
        self.spy.one_arg_method(non_ascii)

        assert_that(self.spy.one_arg_method, called().with_args(non_ascii))

    def test_stub_methods_can_be_handled_separately(self):
        with self.spy:
            self.spy.one_arg_method(1).returns(1000)
            self.spy.two_args_method(5, 5).returns(2000)

        handle1 = self.spy.one_arg_method
        handle2 = self.spy.two_args_method

        self.assertEquals(1000, handle1(1))
        self.assertEquals(2000, handle2(5, 5))
        assert_that(handle1, called().with_args(1))
        assert_that(handle2, called().with_args(5, 5))

    #SAME as VerifiedSpyTests.test_check_unexisting_method
    def test_assert_was_called_with_method_not_in_the_api(self):
        try:
            assert_that(self.spy.unexisting_method, called())
            self.fail("AttributeError should be raised")
        except AttributeError:
            pass

    def test_do_not_call_callable_object_if_wasnt_generated_by_the_framework(self):
        class CallableObj():
            just_testing = True

            def __call__(self, *args, **kwargs):
                raise Exception('should not happen')

        obj = CallableObj()
        with self.spy:
            self.spy.one_arg_method(ANY_ARG).returns(obj)

        self.assertEquals(obj, self.spy.one_arg_method(1),
                          "Wrong returned object")


class pyDoubles__MockTests(TestCase):
    def setUp(self):
        self.mock = Mock(Collaborator)

    def test_fail_on_unexpected_call(self):
        try:
            self.mock.hello()
            self.fail('AssertionError should be raised')
        except AssertionError:
            pass

    def test_fail_on_unexpected_call_msg_is_human_readable(self):
        try:
            self.mock.hello()
        except AssertionError, e:
            assert_that(str(e), contains_string("No one"))

    def test_define_expectation_and_call_method(self):
        with self.mock:
            self.mock.hello()

        self.assertTrue(self.mock.hello() is None)

    def test_define_several_expectatiosn(self):
        with self.mock:
            self.mock.hello()
            self.mock.one_arg_method(ANY_ARG)

        self.assertTrue(self.mock.hello() is None)
        self.assertTrue(self.mock.one_arg_method(1) is None)

    def test_define_expectation_args(self):
        with self.mock:
            self.mock.one_arg_method(1)

        self.assertTrue(self.mock.one_arg_method(1) is None)

    def test_define_expectation_args_and_fail(self):
        with self.mock:
            self.mock.one_arg_method(1)

        try:
            self.mock.one_arg_method(2)
            self.fail('Unexpected call')
        except AssertionError:
            pass

    def test_several_expectations_with_args(self):
        with self.mock:
            self.mock.one_arg_method(1)
            self.mock.two_args_method(2, 3)

        self.assertTrue(self.mock.one_arg_method(1) is None)
        self.assertTrue(self.mock.two_args_method(2, 3) is None)

    def test_expect_call_returning_value(self):
        with self.mock:
            self.mock.one_arg_method(1).returns(1000)

        self.assertEquals(1000, self.mock.one_arg_method(1))

    def test_assert_expectations_are_satisfied(self):
        with self.mock:
            self.mock.hello()

        assert_that(self.mock, is_not(verify()))

    def test_assert_satisfied_when_it_really_is(self):
        with self.mock:
            self.mock.hello()

        self.mock.hello()
        assert_that(self.mock, verify())

    def test_number_of_calls_matter(self):
        with self.mock:
            self.mock.hello()

        self.mock.hello()
        self.mock.hello()

        assert_that(self.mock, is_not(verify()))

    # Not applicable to doublex
#    def test_using_when_or_expect_call_without_double(self):
#        self.failUnlessRaises(WrongApiUsage,
#                        expect_call, Collaborator())

    def test_expectations_on_synonyms(self):
        with self.mock:
            self.mock.one_arg_method(ANY_ARG)

        self.mock.alias_method(1)

        assert_that(self.mock, verify())

    def test_several_expectations_with_different_args(self):
        with self.mock:
            self.mock.one_arg_method(1)
            self.mock.one_arg_method(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        assert_that(self.mock, is_not(verify()))

    def test_expect_several_times(self):
        with self.mock:
            self.mock.one_arg_method(1).times(2)

        self.mock.one_arg_method(1)

        assert_that(self.mock, is_not(verify()))

    def test_expect_several_times_matches_exactly(self):
        with self.mock:
            self.mock.one_arg_method(1).times(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        assert_that(self.mock, verify())

    def test_expect_several_times_without_args_definition(self):
        with self.mock:
            self.mock.one_arg_method(ANY_ARG).times(2)

        self.mock.one_arg_method(1)
        self.mock.one_arg_method(1)

        assert_that(self.mock, verify())

    def test_defend_agains_less_than_2_times(self):
        try:
            with self.mock:
                self.mock.one_arg_method(ANY_ARG).times(0)

            self.fail('times cant be less than 1')
        except WrongApiUsage:
            pass

    def test_times_and_return_value(self):
        with self.mock:
            self.mock.one_arg_method(ANY_ARG).returns(1000).times(2)

        self.assertEquals(1000, self.mock.one_arg_method(1))
        self.assertEquals(1000, self.mock.one_arg_method(1))

        assert_that(self.mock, verify())

    def test_times_and_return_value_and_input_args(self):
        with self.mock:
            self.mock.one_arg_method(10).returns(1000).times(2)

        self.assertEquals(1000, self.mock.one_arg_method(10))
        self.assertEquals(1000, self.mock.one_arg_method(10))

        assert_that(self.mock, verify())


class pyDoubles__MockFromEmptyObjectTests(TestCase):
    def setUp(self):
        self.mock = Mock()

    def test_mock_can_work_from_empty_object(self):
        with self.mock as mock:
            mock.hello()

        self.mock.hello()

        assert_that(self.mock, verify())

    # Not applicable to doublex
    def test_mock_without_args_is_empty_mock(self):
        pass

    def test_several_expectations_in_empty_mock(self):
        with self.mock:
            self.mock.hello()
            self.mock.one_arg_method(1)

        self.mock.hello()
        self.mock.one_arg_method(1)

        assert_that(self.mock, verify())

    def test_several_expectations_with_args_in_empty_mock(self):
        with self.mock:
            self.mock.one_arg_method(1)
            self.mock.one_arg_method(2)

        self.assertTrue(self.mock.one_arg_method(1) is None)
        self.assertTrue(self.mock.one_arg_method(2) is None)

        assert_that(self.mock, verify())


class pyDoubles__StubMethodsTests(TestCase):
    def setUp(self):
        self.collaborator = Collaborator()

    def test_method_returning_value(self):
        self.collaborator.hello = method_returning("bye")

        self.assertEquals("bye", self.collaborator.hello())

    def test_method_args_returning_value(self):
        self.collaborator.one_arg_method = method_returning("bye")

        self.assertEquals("bye", self.collaborator.one_arg_method(1))

    def test_method_raising_exception(self):
        self.collaborator.hello = method_raising(SomeException)
        try:
            self.collaborator.hello()
            self.fail("exception not raised")
        except SomeException:
            pass


class pyDoubles__MatchersTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator)

    def test_str_cotaining_with_exact_match(self):
        with self.spy:
            self.spy.one_arg_method(contains_string("abc")).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method("abc"))

    def test_str_containing_with_substr(self):
        with self.spy:
            self.spy.one_arg_method(contains_string("abc")).returns(1000)

        self.assertEqual(1000, self.spy.one_arg_method("XabcX"))

    def test_str_containing_with_substr_unicode(self):
        with self.spy:
            self.spy.one_arg_method(contains_string("abc")).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method(u"XabcñX"))

    def test_str_containing_but_matcher_not_used(self):
        with self.spy:
            self.spy.one_arg_method("abc").returns(1000)

        self.assertNotEquals(1000, self.spy.one_arg_method("XabcX"))

    def test_was_called_and_substr_matcher(self):
        self.spy.one_arg_method("XabcX")

        assert_that(self.spy.one_arg_method,
                    called().with_args(contains_string("abc")))

    def test_str_not_containing(self):
        with self.spy:
            self.spy.one_arg_method(is_not(contains_string("abc"))).returns(1000)

        self.assertNotEquals(1000, self.spy.one_arg_method("abc"))

    def test_str_not_containing_stubs_anything_else(self):
        with self.spy:
            self.spy.one_arg_method(is_not(contains_string("abc"))).returns(1000)

        self.assertEquals(1000, self.spy.one_arg_method("xxx"))

    def test_str_not_containing_was_called(self):
        self.spy.one_arg_method("abc")
        assert_that(self.spy.one_arg_method,
                    called().with_args(is_not(contains_string("xxx"))))

    def test_several_matchers(self):
        with self.spy:
            self.spy.two_args_method(
                contains_string("abc"),
                contains_string("xxx")).returns(1000)

        self.assertNotEquals(1000,
                             self.spy.two_args_method("abc", "yyy"))

    def test_str_length_matcher(self):
        with self.spy:
            self.spy.one_arg_method(has_length(5)).returns(1000)

        self.assertEquals(1000,
                          self.spy.one_arg_method("abcde"))

    def test_matchers_when_passed_arg_is_none(self):
        with self.spy:
            self.spy.one_arg_method(has_length(5)).returns(1000)

        self.assertTrue(self.spy.one_arg_method(None) is None)

    def test_compare_objects_is_not_possible_without_eq_operator(self):
        class SomeObject():
            field1 = field2 = None

        obj = SomeObject()
        obj2 = SomeObject()
        self.spy.one_arg_method(obj)

        try:
            assert_that(self.spy.one_arg_method, called().with_args(obj2))
            self.fail("they should not match")
        except AssertionError:
            pass

    def test_if_doesnt_match_message_is_human_redable(self):
        self.spy.one_arg_method("XabcX")

        try:
            assert_that(self.spy.one_arg_method,
                        called().with_args(contains_string("xxx")))

        except AssertionError, e:
            assert_that(str(e), contains_string("xxx"))
            assert_that(
                str(e), contains_string("string containing"))

    def test_obj_with_field_matcher(self):
        obj = Collaborator()
        obj.id = 20
        self.spy.one_arg_method(obj)

        assert_that(self.spy.one_arg_method,
                    called().with_args(has_property('id', 20)))

    def test_obj_with_several_fields_matcher(self):
        obj = Collaborator()
        obj.id = 21
        self.spy.one_arg_method(obj)
        try:
            assert_that(
                self.spy.one_arg_method,
                called().with_args(all_of(
                    has_property('id', 20),
                    has_property('test_field', 'OK'))))
            self.fail('Wrong assertion, id field is different')
        except AssertionError:
            pass

#    Not applicable to doublex, cause doublex uses hamcrest matchers
#    def test_obj_with_field_defends_agains_wrong_usage(self):
#        self.spy.one_arg_method(Collaborator())
#        try:
#            assert_that_method(
#                self.spy.one_arg_method).was_called().with_args(
#                obj_with_fields('id = 20'))
#            self.fail('Wrong assertion, argument should be a dictionary')
#        except WrongApiUsage:
#            pass

# NOT APPLICABLE. doubles uses hamcrest matchers
#class pyDoubles__CustomMatchersTest(unittest.TestCase):
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
