# -*- coding:utf-8; tab-width:4; mode:python -*-

# doublex
#
# Copyright © 2012 David Villa Alises
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import time

import sys
from unittest import TestCase
import itertools
import thread
import threading

from hamcrest import is_not, all_of, contains_string, has_length
from hamcrest.library.text.stringcontainsinorder import *
from hamcrest.library.object.hasproperty import *
from hamcrest.library.number.ordering_comparison import *

from doublex import *


class StubTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def test_record_invocation(self):
        with self.stub:
            self.stub.foo().returns(2)

        assert_that(self.stub.foo(), is_(2))

    def test_using_alias_in_context(self):
        with self.stub as stub:
            stub.foo().returns(2)

        assert_that(self.stub.foo(), is_(2))

    def test_creating_double_with_context(self):
        with Stub() as stub:
            stub.foo().returns(2)

        assert_that(stub.foo(), is_(2))

    def test_record_invocation_with_args(self):
        with self.stub:
            self.stub.foo(1, param='hi').returns(2)

        assert_that(self.stub.foo(1, param='hi'), is_(2))

    def test_record_invocation_with_wrong_args_returns_None(self):
        with self.stub:
            self.stub.foo(1, param='hi').returns(2)

        assert_that(self.stub.foo(1, param='wrong'), is_(None))

    def test_not_stubbed_method_returns_None(self):
        with self.stub:
            self.stub.foo().returns(True)

        assert_that(self.stub.bar(), is_(None))

    def test_raises(self):
        with self.stub:
            self.stub.foo().raises(KeyError)

        try:
            self.stub.foo()
            self.fail("It should raise KeyError")
        except KeyError:
            pass


class VerifiedStubTests(TestCase):
    def setUp(self):
        self.stub = Stub(Collaborator)

    def test_stubbing_a_existing_method(self):
        with self.stub:
            self.stub.hello().returns("bye")

        assert_that(self.stub.hello(), is_("bye"))

    def test_from_instance(self):
        stub = Stub(Collaborator())
        with stub:
            stub.hello().returns("bye")

        assert_that(stub.hello(), is_("bye"))

    def test_stubbing_a_unexisting_method_raises_error(self):
        try:
            with self.stub:
                self.stub.wrong().returns("bye")

        except AttributeError as e:
            expected = "'Collaborator' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))

    def test_stubbing_with_wrong_args_raises_error(self):
        try:
            with self.stub:
                self.stub.hello(1).returns("bye")

        except TypeError as e:
            expected = "hello() takes exactly 1 argument (2 given)"
            if sys.version_info >= (3,):
                expected = "hello() takes exactly 1 positional argument (2 given)"
            assert_that(str(e), contains_string(expected))

    # bitbucket issue #6
    def test_keyworked_or_positional(self):
        with self.stub:
            self.stub.kwarg_method(1).returns(1000)
            self.stub.kwarg_method(key_param=2).returns(2000)

        assert_that(self.stub.kwarg_method(1), is_(1000))
        assert_that(self.stub.kwarg_method(key_param=2), is_(2000))


class StubReturnValueTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator)

    def test_returning_tuple(self):
        with self.spy:
            self.spy.hello().returns((3, 4))

        assert_that(self.spy.hello(), (3, 4))


class AdhocAttributesTests(TestCase):
    "all doubles accepts ad-hoc attributes"

    def test_add_attribute_for_free_stub(self):
        stub = Stub()
        stub.foo = 1

    def test_add_attribute_for_verified_stub(self):
        stub = Stub(Collaborator)
        stub.foo = 1

    def test_add_attribute_for_free_spy(self):
        stub = Spy()
        stub.foo = 1

    def test_add_attribute_for_verified_spy(self):
        stub = Spy(Collaborator)
        stub.foo = 1

    def test_add_attribute_for_free_mock(self):
        stub = Mock()
        stub.foo = 1

    def test_add_attribute_for_verified_mock(self):
        stub = Mock(Collaborator)
        stub.foo = 1

class SpyTests(TestCase):
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
        assert_that(self.spy.foo, is_not(called().times(1)))
        assert_that(self.spy.foo, is_not(called().times(3)))

    def test_called_without_args(self):
        self.spy.foo()

        assert_that(self.spy.foo, called().with_args())

    def test_called_with_None(self):
        self.spy.foo(None)

        assert_that(self.spy.foo, called().with_args(None))
        assert_that(self.spy.foo, is_not(called().with_args()))

    def test_not_called_without_args(self):
        self.spy.foo(1)

        assert_that(self.spy.foo, is_not(called().with_args()))

    def test_called_with_specified_args(self):
        self.spy.foo(1)

        assert_that(self.spy.foo, called().with_args(1))

    def test_not_called_with_specified_args(self):
        self.spy.foo()
        self.spy.foo(2)

        assert_that(self.spy.foo, is_not(called().with_args(1)))

    def test_mixed_args(self):
        self.spy.send_mail('hi')
        self.spy.send_mail('foo@bar.net')

        assert_that(self.spy.send_mail, called())
        assert_that(self.spy.send_mail, called().times(2))
        assert_that(self.spy.send_mail, called().with_args('foo@bar.net'))

    def test_called_with_several_types_and_kargs(self):
        self.spy.foo(3.0, [1, 2], 'hi', color='red', width=10)

        assert_that(self.spy.foo, called().with_args(
                3.0, [1, 2], 'hi', color='red', width=10))
        assert_that(self.spy.foo, called().with_args(
                3.0, [1, 2], 'hi', width=10, color='red'))
        assert_that(self.spy.foo, is_not(called().with_args(
                [1, 2], 'hi', width=10, color='red')))
        assert_that(self.spy.foo, is_not(called().with_args(
                [1, 2], 3.0, 'hi', width=10, color='red')))

    def test_called_with_args_and_times(self):
        self.spy.foo(1)
        self.spy.foo(1)
        self.spy.foo(2)

        assert_that(self.spy.foo, called().with_args(1).times(2))
        assert_that(self.spy.foo, called().with_args(2))
        assert_that(self.spy.foo, called().times(3))

#    def test_called_anything_and_value(self):
#        spy = Spy(Collaborator)
#        spy.two_args_method(10, 20)
#        assert_that(spy.two_args_method, called().with_args(anything(), 20))
#
#    def test_called_name_arg_value(self):
#        spy = Spy(Collaborator)
#        spy.two_args_method(10, 20)
#        assert_that(spy.two_args_method, called().with_args(arg2=20))
#
#    def test_called_karg(self):
#        spy = Spy(Collaborator)
#        spy.mixed_method(2, True)
#        assert_that(spy.mixed_method, called().with_args(key_param=True))


class VerifiedSpyTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator())

    def test_from_instance(self):
        spy = Spy(Collaborator())
        spy.hello()

        assert_that(spy.hello, called())

    def test_call_unexisting_method(self):
        try:
            self.spy.wrong()
            self.fail('AttributeError should be raised')
        except AttributeError as e:
            expected = "'Collaborator' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))

    def test_check_unexisting_method(self):
        try:
            assert_that(self.spy.wrong, called())
            self.fail('AttributeError should be raised')
        except AttributeError as e:
            expected = "'Collaborator' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))

    def test_create_from_oldstyle_class(self):
        Spy(Collaborator)

    def test_create_from_newstyle_class(self):
        Spy(ObjCollaborator)


class BuiltinSpyTests(TestCase):
    def test_builtin_method(self):
        spy = Spy(list)
        spy.append(10)
        assert_that(spy.append, called().with_args(10))

    def test_builtin_method_wrong_num_args(self):
        spy = Spy(list)
        try:
            spy.append(10, 20)
            self.fail('AttributeError should be raised')
        except TypeError as e:
            expected = "list.append() takes exactly 1 argument (2 given)"
            assert_that(str(e), contains_string(expected))

    def test_wrong_builtin_method(self):
        spy = Spy(list)
        try:
            spy.wrong(10)
            self.fail('AttributeError should be raised')
        except AttributeError as e:
            expected = "'list' object has no attribute 'wrong'"
            assert_that(str(e), contains_string(expected))


class ProxySpyTest(TestCase):
    def test_must_give_argument(self):
        self.failUnlessRaises(TypeError, ProxySpy)

    def test_given_argument_can_not_be_oldstyle_class(self):
        self.failUnlessRaises(TypeError,
                              ProxySpy, Collaborator)

    def test_given_argument_can_not_be_newstyle_class(self):
        self.failUnlessRaises(TypeError,
                              ProxySpy, ObjCollaborator)

    def test_propagate_stubbed_calls_to_collaborator(self):
        class Foo:
            def __init__(self):
                self.value = 0

            def store_add(self, value):
                self.value = value
                return value + 1

        foo = Foo()
        with ProxySpy(foo) as spy:
            spy.store_add(3).returns(1000)

        assert_that(spy.store_add(2), is_(3))
        assert_that(foo.value, is_(2))
        assert_that(spy.store_add(3), is_(1000))
        assert_that(foo.value, is_(3))


class MockOrderTests(TestCase):
    def setUp(self):
        self.mock = Mock()

    def test_order_matters__ok(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        self.mock.foo()
        self.mock.bar()

        assert_that(self.mock, verify())

    def test_order_matters__fail(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        self.mock.bar()
        self.mock.foo()

        self.failUnlessRaises(
            AssertionError,
            assert_that, self.mock, verify())

    def test_method_name_order_does_not_matter_with_any_order(self):
        with self.mock:
            self.mock.foo()
            self.mock.bar()

        self.mock.bar()
        self.mock.foo()

        assert_that(self.mock, any_order_verify())

    def test_args_order_does_not_matter_with_any_order(self):
        with self.mock:
            self.mock.foo(2)
            self.mock.foo(1)

        self.mock.foo(1)
        self.mock.foo(2)

        assert_that(self.mock, any_order_verify())

    def test_kwargs_order_does_not_matter_with_any_order(self):
        with self.mock:
            self.mock.foo(1, key='a')
            self.mock.foo(1, key='b')

        self.mock.foo(1, key='b')
        self.mock.foo(1, key='a')

        assert_that(self.mock, any_order_verify())


class VerifiedMockTests(TestCase):
    def test_from_instance(self):
        mock = Mock(Collaborator())
        with mock:
            mock.hello()

        mock.hello()

        assert_that(mock, verify())


class DisplayResultsTests(TestCase):
    def setUp(self):
        with Spy() as self.empty_spy:
            self.empty_spy.foo(ANY_ARG).returns(True)

        with Spy(Collaborator) as self.spy:
            self.spy.method_one(ANY_ARG).returns(2)

    def test_empty_spy_stub_method(self):
        assert_that(self.empty_spy.foo.show_history(),
                    "method 'Spy.foo' never invoked")

    def test_spy_stub_method(self):
        assert_that(self.spy.method_one.show_history(),
                    "method 'Collaborator.method_one' never invoked")

    def test_empty_spy_stub_method_invoked(self):
        self.empty_spy.foo()
        expected = [
            "method 'Spy.foo' was invoked",
            "foo()"]
        assert_that(self.empty_spy.foo.show_history(),
                    string_contains_in_order(*expected))

    def test_spy_stub_method_invoked(self):
        self.spy.method_one(1)
        expected = [
            "method 'Collaborator.method_one' was invoked",
            'method_one(1)']
        assert_that(self.spy.method_one.show_history(),
                    string_contains_in_order(*expected))

    def test_empty_spy_non_stubbed_method_invoked(self):
        self.empty_spy.bar(1, 3.0, "text", key1="text", key2=[1, 2])
        expected = [
            "method 'Spy.bar' was invoked",
            "bar(1, 3.0, 'text', key1='text', key2=[1, 2])"]
        assert_that(self.empty_spy.bar.show_history(),
                    string_contains_in_order(*expected))

    def test_spy_several_invoked_same_method(self):
        self.spy.mixed_method(5, True)
        self.spy.mixed_method(8, False)

        expected = "method 'Collaborator.mixed_method' was invoked"
        assert_that(self.spy.mixed_method.show_history(),
                    contains_string(expected))


class FrameworApiTest(TestCase):
    def test_called_requires_spy(self):
        stub = Stub()
        try:
            assert_that(stub.method, called())
            self.fail('exception should be raised')
        except WrongApiUsage as e:
            assert_that(str(e), contains_string('takes a spy method (got'))


class ApiMismatchTest(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator)

    def test_default_params(self):
        self.spy.mixed_method(1)

    def test_give_karg(self):
        self.spy.mixed_method(1, key_param=True)

    def test_give_karg_without_key(self):
        self.spy.mixed_method(1, True)

    def test_fail_missing_method(self):
        try:
            self.spy.missing()
            self.fail("TypeError should be raised")

        except AttributeError as e:
            expected = "'Collaborator' object has no attribute 'missing'"
            assert_that(str(e), contains_string(expected))

    def test_fail_wrong_args(self):
        try:
            self.spy.hello("wrong")
            self.fail("TypeError should be raised")

        except TypeError as e:
            expected = "Collaborator.hello() takes exactly 1 argument (2 given)"
            if sys.version_info >= (3,):
                expected = "Collaborator.hello() takes exactly 1 positional argument (2 given)"
            assert_that(str(e), contains_string(expected))

    def test_fail_wrong_kargs(self):
        try:
            self.spy.kwarg_method(wrong_key=1)
            self.fail("TypeError should be raised")

        except TypeError as e:
            expected = "Collaborator.kwarg_method() got an unexpected keyword argument 'wrong_key'"
            assert_that(str(e), contains_string(expected))


class ANY_ARG_StubTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def test_any_args(self):
        with self.stub:
            self.stub.foo(ANY_ARG).returns(True)

        assert_that(self.stub.foo(), is_(True))
        assert_that(self.stub.foo(1), is_(True))
        assert_that(self.stub.foo(key1='a'), is_(True))
        assert_that(self.stub.foo(1, 2, 3, key1='a', key2='b'), is_(True))

    def test_fixed_args_and_any_args(self):
        with self.stub:
            self.stub.foo(1, ANY_ARG).returns(True)

        assert_that(self.stub.foo(1, 2, 3), is_(True))
        assert_that(self.stub.foo(1, key1='a'), is_(True))


class ANY_ARG_SpyTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_no_args(self):
        self.spy.foo()
        assert_that(self.spy.foo, called().with_args(ANY_ARG))

    def test_one_arg(self):
        self.spy.foo(1)
        assert_that(self.spy.foo, called().with_args(ANY_ARG))

    def test_one_karg(self):
        self.spy.foo(key='val')
        assert_that(self.spy.foo, called().with_args(ANY_ARG))

    def test_three_args(self):
        self.spy.foo(1, 2, 3)
        assert_that(self.spy.foo, called().with_args(1, ANY_ARG))
        assert_that(self.spy.foo, never(called().with_args(2, ANY_ARG)))

    def test_args_and_kargs(self):
        self.spy.foo(1, 2, 3, key1='a', key2='b')
        assert_that(self.spy.foo, called().with_args(1, ANY_ARG))
        assert_that(self.spy.foo, never(called().with_args(2, ANY_ARG)))

    def test__called__and__called_with_args__ANY_ARGS_is_the_same(self):
        self.spy.foo()
        self.spy.foo(3)
        self.spy.foo('hi')
        self.spy.foo(None)

        assert_that(self.spy.foo, called().times(4))
        assert_that(self.spy.foo, called().with_args(ANY_ARG).times(4))


class MatcherTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_check_has_length(self):
        self.spy.foo("abcd")

        assert_that(self.spy.foo, called().with_args(has_length(4)))
        assert_that(self.spy.foo, called().with_args(has_length(greater_than(3))))
        assert_that(self.spy.foo, called().with_args(has_length(less_than(5))))
        assert_that(self.spy.foo,
                    is_not(called().with_args(has_length(greater_than(5)))))

    def test_stub_has_length(self):
        with self.spy:
            self.spy.foo(has_length(less_than(4))).returns('<4')
            self.spy.foo(has_length(4)).returns('four')
            self.spy.foo(
                has_length(
                    all_of(greater_than(4),
                           less_than(8)))).returns('4<x<8')
            self.spy.foo(has_length(greater_than(8))).returns('>8')

        assert_that(self.spy.foo((1, 2)), is_('<4'))
        assert_that(self.spy.foo('abcd'), is_('four'))
        assert_that(self.spy.foo('abcde'), is_('4<x<8'))
        assert_that(self.spy.foo([0] * 9), is_('>8'))

    def test_stub_contains_string(self):
        with Stub() as stub:
            stub.method(contains_string("some")).returns(1000)

        assert_that(stub.method("awesome"), is_(1000))

    # doc
    def test_times_arg_may_be_matcher(self):
        self.spy.foo()
        self.spy.foo(1)
        self.spy.foo(1)
        self.spy.foo(2)

        assert_that(self.spy.never, is_not(called()))                    # = 0 times
        assert_that(self.spy.foo, called())                              # > 0
        assert_that(self.spy.foo, called().times(greater_than(0)))       # > 0 (same)
        assert_that(self.spy.foo, called().times(4))                     # = 4
        assert_that(self.spy.foo, called().times(greater_than(2)))       # > 2
        assert_that(self.spy.foo, called().times(less_than(6)))          # < 6

        assert_that(self.spy.foo, is_not(called().with_args(5)))                 # = 0 times
        assert_that(self.spy.foo, called().with_args().times(1))                 # = 1
        assert_that(self.spy.foo, called().with_args(anything()))                # > 0
        assert_that(self.spy.foo, called().with_args(anything()).times(4))       # = 4
        assert_that(self.spy.foo, called().with_args(1).times(2))                # = 2
        assert_that(self.spy.foo, called().with_args(1).times(greater_than(1)))  # > 1
        assert_that(self.spy.foo, called().with_args(1).times(less_than(5)))     # < 5

    # doc
    def test_called_args(self):
        self.spy.m1()
        self.spy.m2(None)
        self.spy.m3(2)
        self.spy.m4("hi", 3.0)
        self.spy.m5([1, 2])
        self.spy.m6(name="john doe")

        assert_that(self.spy.m1, called())
        assert_that(self.spy.m2, called())

        assert_that(self.spy.m1, called().with_args())
        assert_that(self.spy.m2, called().with_args(None))
        assert_that(self.spy.m3, called().with_args(2))
        assert_that(self.spy.m4, called().with_args("hi", 3.0))
        assert_that(self.spy.m5, called().with_args([1, 2]))
        assert_that(self.spy.m6, called().with_args(name="john doe"))

        assert_that(self.spy.m3, called().with_args(less_than(3)))
        assert_that(self.spy.m3, called().with_args(greater_than(1)))
        assert_that(self.spy.m6, called().with_args(name=contains_string("doe")))


class StubObserverTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def test_observer_called(self):
        observer = Observer()
        self.stub.foo.attach(observer.update)
        self.stub.foo(2)

        assert_that(observer.state, is_(2))

    def test_observer_called_tested_using_a_doublex_spy(self):
        observer = Spy()
        self.stub.foo.attach(observer.update)
        self.stub.foo(2)

        assert_that(observer.update, called().with_args(2))


class StubDelegateTests(TestCase):
    def setUp(self):
        self.stub = Stub()

    def assert_012(self, method):
        for x in range(3):
            assert_that(method(), is_(x))

    def test_delegate_to_other_method(self):
        with self.stub:
            self.stub.foo().delegates(Collaborator().hello)

        assert_that(self.stub.foo(), is_("hello"))

    def test_delegate_to_list(self):
        with self.stub:
            self.stub.foo().delegates(range(3))

        self.assert_012(self.stub.foo)

    def test_delegate_to_generator(self):
        with self.stub:
            self.stub.foo().delegates(x for x in range(3))

        self.assert_012(self.stub.foo)

    def test_delegate_to_count(self):
        with self.stub:
            self.stub.foo().delegates(itertools.count())

        self.assert_012(self.stub.foo)

    def test_delegate_to_lambda(self):
        with self.stub:
            self.stub.foo().delegates(lambda: 2)

        assert_that(self.stub.foo(), is_(2))

    def test_delegate_to_another_stub(self):
        stub2 = Stub()
        with stub2:
            stub2.bar().returns("hi!")

        with self.stub:
            self.stub.foo().delegates(stub2.bar)

        assert_that(self.stub.foo(), is_("hi!"))

    def test_not_delegable_object(self):
        try:
            with self.stub:
                self.stub.foo().delegates(None)
            fail("Exception should be raised")

        except WrongApiUsage as e:
            expected = "delegates() must be called with callable or iterable instance (got 'None' instead)"
            assert_that(str(e), contains_string(expected))


class MockDelegateTest(TestCase):
    def setUp(self):
        self.mock = Mock()

    def assert_012(self, method):
        for x in range(3):
            assert_that(method(), is_(x))

    def test_delegate_to_list_is_only_an_expectation(self):
        with self.mock:
            self.mock.foo().delegates(range(3))

        self.mock.foo()
        assert_that(self.mock, verify())


class MimicTests(TestCase):
    class A(object):
        def method_a(self, n):
            return n + 1

    class B(A):
        def method_b(self):
            return "hi"

    def test_normal_spy_does_not_inherit_collaborator_superclasses(self):
        spy = Spy(self.B)
        assert_that(not isinstance(spy, self.B))

    def test_mimic_spy_DOES_inherit_collaborator_superclasses(self):
        spy = Mimic(Spy, self.B)
        for cls in [self.B, self.A, Spy, Stub, object]:
            assert_that(isinstance(spy, cls), cls)

    def test_mimic_stub_works(self):
        stub = Mimic(Stub, self.B)
        with stub:
            stub.method_a(2).returns(3)

        assert_that(stub.method_a(2), is_(3))

    def test_mimic_stub_from_instance(self):
        stub = Mimic(Stub, self.B())
        with stub:
            stub.method_a(2).returns(3)

        assert_that(stub.method_a(2), is_(3))

    def test_mimic_spy_works(self):
        spy = Mimic(Spy, self.B)
        with spy:
            spy.method_a(5).returns(True)

        assert_that(spy.method_a(5), is_(True))

        assert_that(spy.method_a, called())
        assert_that(spy.method_a, called().with_args(5))

    def test_mimic_proxy_spy_works(self):
        spy = Mimic(ProxySpy, self.B())
        assert_that(spy.method_a(5), is_(6))

        assert_that(spy.method_a, called())
        assert_that(spy.method_a, called().with_args(5))

    def test_mimic_mock_works(self):
        mock = Mimic(Mock, self.B)
        with mock:
            mock.method_a(2)

        mock.method_a(2)

        assert_that(mock, verify())


class PropertyTests(TestCase):
    def test_stub_notset_property_is_None(self):
        stub = Stub(ObjCollaborator)
        assert_that(stub.prop, is_(None))

    def test_stub_property(self):
        stub = Stub(ObjCollaborator)
        with stub:
            stub.prop = 2

        assert_that(stub.prop, is_(2))

    def test_spy_get_property(self):
        spy = Spy(ObjCollaborator)
        skip = spy.prop
        assert_that(spy, property_got('prop'))

    def test_spy_not_get_property(self):
        spy = Spy(ObjCollaborator)
        assert_that(spy, never(property_got('prop')))

    def test_spy_get_property_fail(self):
        spy = Spy(ObjCollaborator)
        self.failUnlessRaises(
            AssertionError,
            assert_that, spy, property_got('prop'))

    def test_spy_set_property(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 2
        assert_that(spy, property_set('prop'))

    def test_spy_not_set_property(self):
        spy = Spy(ObjCollaborator)
        assert_that(spy, never(property_set('prop')))

    def test_spy_set_property_fail(self):
        spy = Spy(ObjCollaborator)
        self.failUnlessRaises(
            AssertionError,
            assert_that, spy, property_set('prop'))

    def test_spy_set_property_to(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 2
        assert_that(spy, property_set('prop').to(2))
        assert_that(spy, never(property_set('prop').to(5)))

    def test_spy_set_property_times(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 2
        spy.prop = 3
        assert_that(spy, property_set('prop').to(2))
        assert_that(spy, property_set('prop').to(3))
        assert_that(spy, property_set('prop').times(2))

    def test_spy_set_property_to_times(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 3
        spy.prop = 3
        assert_that(spy, property_set('prop').to(3).times(2))

    def test_properties_are_NOT_shared_among_doubles(self):
        stub1 = Stub(ObjCollaborator)
        stub2 = Stub(ObjCollaborator)

        stub1.prop = 1000
        assert_that(stub2.prop, is_not(1000))
        assert_that(stub1.__class__ is not stub2.__class__)

    def test_spy_get_readonly_property_with_deco(self):
        spy = Spy(ObjCollaborator)
        skip = spy.prop_deco_readonly
        assert_that(spy, property_got('prop_deco_readonly'))

    def test_spy_SET_readonly_property_with_deco(self):
        spy = Spy(ObjCollaborator)
        try:
            spy.prop_deco_readonly = 'wrong'
            self.fail('should raise exception')
        except AttributeError:
            pass

    def test_hamcrest_matchers(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 2
        spy.prop = 3
        assert_that(spy, property_set('prop').to(greater_than(1)).times(less_than(3)))


class AsyncTests(TestCase):
    class SUT(object):
        def __init__(self, collaborator):
            self.collaborator = collaborator

        def send_data(self, data=0):
            thread.start_new_thread(self.collaborator.write, (data,))

    def test_spy_call_without_async_feature(self):
        # given
        barrier = threading.Event()
        with Spy() as spy:
            spy.write.attach(lambda *args: barrier.set)

        sut = AsyncTests.SUT(spy)

        # when
        sut.send_data()
        barrier.wait(1)    # test probably FAILS without this

        # then
        assert_that(spy.write, called())

    def test_spy_call_with_async_feature(self):
        # given
        spy = Spy()
        sut = AsyncTests.SUT(spy)

        # when
        sut.send_data()

        # then
        assert_that(spy.write, called().async(timeout=1))

    def test_spy_async_call_fluent_methods(self):
        spy = Spy()
        sut = AsyncTests.SUT(spy)

        sut.send_data(3)
        sut.send_data(3)

        # then
        with self.assertRaises(WrongApiUsage):
            assert_that(spy.write, called().async(timeout=1).with_args(3).times(2))


class Observer(object):
    def __init__(self):
        self.state = None

    def update(self, *args, **kargs):
        self.state = args[0]


class ObjCollaborator(object):
    def __init__(self):
        self._propvalue = 1

    def no_args(self):
        return 1

    def prop_getter(self):
        return self._propvalue

    def prop_setter(self, value):
        self._propvalue = value

    prop = property(prop_getter, prop_setter)

    @property
    def prop_deco_readonly(self):
        return 2


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
