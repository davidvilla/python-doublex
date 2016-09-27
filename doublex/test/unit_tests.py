# -*- coding:utf-8; tab-width:4; mode:python -*-

# doublex
#
# Copyright © 2012,2013 David Villa Alises
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


import sys
import itertools
import threading
import thread

if sys.version_info >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase

if sys.version_info >= (3, 0):
    unicode = str
    from io import StringIO
else:
    from io import BytesIO as StringIO


from hamcrest import (
    is_, is_not, instance_of, all_of, has_length, has_entry, starts_with,
    anything, greater_than, less_than,
    contains_string, string_contains_in_order)

from doublex import (
    set_default_behavior,
    ANY_ARG,
    assert_that,
    when, called, never,
    Stub, Spy, ProxySpy, Mock, Tracer, Mimic,
    property_set, property_got,
    method_returning, method_raising, expect_call, verify, any_order_verify,
    WrongApiUsage
    )

from doublex.matchers import MatcherRequiredError
from doublex.internal import InvocationContext


class InvocationContextTests(TestCase):
    def test_order(self):
        c1 = InvocationContext(1)
        c2 = InvocationContext(2)
        contexts = [c2, c1]

        contexts.sort()

        assert_that(contexts[0], is_(c1))

    def test_order_ANY_ARG(self):
        c1 = InvocationContext(1)
        c2 = InvocationContext(ANY_ARG)
        contexts = [c2, c1]

        contexts.sort()

        assert_that(contexts[0], is_(c1))


class FreeStubTests(TestCase):
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

        assert_that(self.stub.unknown(), is_(None))

    def test_returns_input(self):
        with Stub() as stub:
            stub.foo(1).returns_input()

        assert_that(stub.foo(1), is_(1))

    # new on 1.8.2
    def test_returns_input_two_args(self):
        with Stub() as stub:
            stub.foo(ANY_ARG).returns_input()

        assert_that(stub.foo(1, 2), is_((1, 2)))

    def test_raises(self):
        with self.stub:
            self.stub.foo(2).raises(SomeException)

        try:
            self.stub.foo(2)
            self.fail("It should raise SomeException")
        except SomeException:
            pass


class StubTests(TestCase):
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
            if sys.version_info >= (3, 3):
                expected = "hello() takes 1 positional argument but 2 were given"
            assert_that(str(e), contains_string(expected))

    # bitbucket issue #6
    def test_keyword_or_positional(self):
        with self.stub:
            self.stub.kwarg_method(1).returns(1000)
            self.stub.kwarg_method(2).returns(2000)
            self.stub.kwarg_method(key_param=6).returns(6000)

        assert_that(self.stub.kwarg_method(1), is_(1000))
        assert_that(self.stub.kwarg_method(2), is_(2000))
        assert_that(self.stub.kwarg_method(key_param=6), is_(6000))
        assert_that(self.stub.kwarg_method(key_param=6), is_(6000))

    # new on 1.7
    def test_keyworked_or_positional_are_equivalent(self):
        with self.stub:
            self.stub.kwarg_method(1).returns(1000)
            self.stub.kwarg_method(key_param=6).returns(6000)

        assert_that(self.stub.kwarg_method(1), is_(1000))
        assert_that(self.stub.kwarg_method(key_param=1), is_(1000))
        assert_that(self.stub.kwarg_method(6), is_(6000))
        assert_that(self.stub.kwarg_method(key_param=6), is_(6000))

    def test_last_stubbed_method_prevails(self):
        with self.stub:
            self.stub.hello().returns("hi!")

        with self.stub:
            self.stub.hello().returns("bye!")

        assert_that(self.stub.hello(), is_("bye!"))

    def test_last_stubbed_method_prevails_same_with(self):
        with self.stub:
            self.stub.hello().returns("hi!")
            self.stub.hello().returns("bye!")

        assert_that(self.stub.hello(), is_("bye!"))

    def test_returning_tuple(self):
        with self.stub:
            self.stub.hello().returns((3, 4))

        assert_that(self.stub.hello(), is_((3, 4)))


class AccessingActualAttributes(TestCase):
    def test_read_class_attribute_providing_class(self):
        stub = Stub(Collaborator)
        assert_that(stub.class_attr, is_("OK"))

    def test_read_class_attribute_providing_instance(self):
        stub = Stub(Collaborator())
        assert_that(stub.class_attr, is_("OK"))

    # New in 1.6.5
    def test_proxyspy_read_instance_attribute(self):
        stub = Stub(Collaborator())
        assert_that(stub.instance_attr, is_(300))


class AdhocAttributesTests(TestCase):
    "all doubles accepts ad-hoc attributes"

    def test_add_attribute_for_free_stub(self):
        sut = Stub()
        sut.adhoc = 1

    def test_add_attribute_for_verified_stub(self):
        sut = Stub(Collaborator)
        sut.adhoc = 1

    def test_add_attribute_for_free_spy(self):
        sut = Spy()
        sut.adhoc = 1

    def test_add_attribute_for_verified_spy(self):
        sut = Spy(Collaborator)
        sut.adhoc = 1

    def test_add_attribute_for_proxyspy(self):
        sut = ProxySpy(Collaborator())
        sut.adhoc = 1

    def test_add_attribute_for_free_mock(self):
        sut = Mock()
        sut.adhoc = 1

    def test_add_attribute_for_verified_mock(self):
        sut = Mock(Collaborator)
        sut.adhoc = 1


class FreeSpyTests(TestCase):
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


class Spy_calls_tests(TestCase):
    def test_list_recorded_calls(self):
        class Collaborator:
            def method(self, *args, **kargs):
                pass

        with Spy(Collaborator) as spy:
            spy.method(ANY_ARG).returns(100)

        spy.method(1, 2, 3)
        spy.method(key=2, val=5)

        assert_that(spy.method.calls[0].args, is_((1, 2, 3)))
        assert_that(spy.method.calls[1].kargs, is_(dict(key=2, val=5)))
        assert_that(spy.method.calls[1].retval, is_(100))

    def test_called_with_an_object(self):
        class Module:
            def getName(self):
                return "Module"

        class Visitor:
            def visitModule(self, m):
                pass

        class Parser:
            def __init__(self, visitor):
                self.visitor = visitor

            def accept(self, visitor):
                self.visitor.visitModule(Module())

        visitor = Spy(Visitor)
        parser = Parser(visitor)
        parser.accept(visitor)

        assert_that(visitor.visitModule.calls[0].args[0].getName(), is_("Module"))


class SpyTests(TestCase):
    def setUp(self):
        self.spy = Spy(Collaborator)

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

    def test_wrong_call_args(self):
        self.spy.hello()
        with self.assertRaises(TypeError):
            assert_that(self.spy.hello, called().with_args('some'))


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

    def test_dict_builtin_method(self):
        spy = Spy(dict)
        spy.__setitem__(3, 5)
        assert_that(spy.__setitem__, called().with_args(3, 5))


class ProxySpyTests(TestCase):
    def test_must_give_argument(self):
        with self.assertRaises(TypeError):
            ProxySpy()

    def test_given_argument_can_not_be_oldstyle_class(self):
        with self.assertRaises(TypeError):
            ProxySpy(Collaborator)

    def test_given_argument_can_not_be_newstyle_class(self):
        with self.assertRaises(TypeError):
            ProxySpy(ObjCollaborator)

    def test_propagate_stubbed_calls_to_collaborator(self):
        class Foo:
            def __init__(self):
                self.value = 0

            def store_add(self, value):
                self.value = value
                return -value

        foo = Foo()
        with ProxySpy(foo) as spy:
            spy.store_add(3).returns(1000)

        assert_that(spy.store_add(2), is_(-2))
        assert_that(foo.value, is_(2))
        assert_that(spy.store_add(3), is_(1000))
        assert_that(foo.value, is_(3))


class MockTests(TestCase):
    def test_with_args(self):
        mock = Mock()
        with mock:
            mock.hello(1)
            mock.bye(2)
            mock.bye(3)

        mock.hello(1)
        mock.bye(2)
        mock.bye(3)

        assert_that(mock, verify())

    def test_with_several_args(self):
        mock = Mock()
        with mock:
            mock.hello(1, 1)
            mock.bye(2, 2)
            mock.bye(3, 3)

        mock.hello(1, 1)
        mock.bye(2, 2)
        mock.bye(3, 3)

        assert_that(mock, verify())

    def test_with_kargs(self):
        mock = Mock()
        with mock:
            mock.hello(1, name=1)
            mock.bye(2, value=2)
            mock.bye(3, value=3)

        mock.hello(1, name=1)
        mock.bye(2, value=2)
        mock.bye(3, value=3)

        assert_that(mock, verify())

    def test_from_instance(self):
        mock = Mock(Collaborator())
        with mock:
            mock.hello()

        mock.hello()

        assert_that(mock, verify())


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

        with self.assertRaises(AssertionError):
            assert_that(self.mock, verify())

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

    def test_several_args_with_any_order(self):
        with self.mock:
            self.mock.foo(2, 2)
            self.mock.bar(1)
            self.mock.foo(1, 1)
            self.mock.bar(2)

        self.mock.foo(1, 1)
        self.mock.bar(1)
        self.mock.foo(2, 2)
        self.mock.bar(2)

        assert_that(self.mock, any_order_verify())

    def test_several_args_with_matcher_any_order(self):
        with self.mock:
            self.mock.foo(2, anything())
            self.mock.bar(1)
            self.mock.foo(1, anything())
            self.mock.bar(2)

        self.mock.foo(1, 1)
        self.mock.bar(1)
        self.mock.foo(2, 2)
        self.mock.bar(2)

        assert_that(self.mock, any_order_verify())


class DisplayResultsTests(TestCase):
    def setUp(self):
        with Spy() as self.empty_spy:
            self.empty_spy.foo(ANY_ARG).returns(True)

        with Spy(Collaborator) as self.spy:
            self.spy.method_one(ANY_ARG).returns(2)

    def test_empty_spy_stub_method(self):
        assert_that(self.empty_spy.foo._show_history(),
                    reason="method 'Spy.foo' never invoked")

    def test_spy_stub_method(self):
        assert_that(self.spy.method_one._show_history(),
                    reason="method 'Collaborator.method_one' never invoked")

    def test_empty_spy_stub_method_invoked(self):
        self.empty_spy.foo()
        expected = [
            "method 'Spy.foo' was invoked",
            "foo()"]
        assert_that(self.empty_spy.foo._show_history(),
                    string_contains_in_order(*expected))

    def test_spy_stub_method_invoked(self):
        self.spy.method_one(1)
        expected = [
            "method 'Collaborator.method_one' was invoked",
            'method_one(1)']
        assert_that(self.spy.method_one._show_history(),
                    string_contains_in_order(*expected))

    def test_empty_spy_non_stubbed_method_invoked(self):
        self.empty_spy.bar(1, 3.0, "text", key1="text", key2=[1, 2])
        expected = [
            "method 'Spy.bar' was invoked",
            "bar(1, 3.0, 'text', key1='text', key2=[1, 2])"]
        assert_that(self.empty_spy.bar._show_history(),
                    string_contains_in_order(*expected))

    def test_spy_several_invoked_same_method(self):
        self.spy.mixed_method(5, True)
        self.spy.mixed_method(8, False)

        expected = "method 'Collaborator.mixed_method' was invoked"
        assert_that(self.spy.mixed_method._show_history(),
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
            if sys.version_info >= (3, 3):
                expected = "hello() takes 1 positional argument but 2 were given"
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

    def test_ANY_ARG_must_be_last_positional_argument(self):
        with self.assertRaises(WrongApiUsage):
            with self.stub:
                self.stub.method(1, ANY_ARG, 3).returns(True)


class ANY_ARG_SpyTests(TestCase):
    def setUp(self):
        self.spy = Spy()

    def test_no_args(self):
        self.spy.foo()
        assert_that(self.spy.foo, called().with_args(ANY_ARG))
        assert_that(self.spy.foo, never(called().with_args(anything())))

    def test_one_arg(self):
        self.spy.foo(1)
        assert_that(self.spy.foo, called())
        assert_that(self.spy.foo, called().with_args(ANY_ARG))
        assert_that(self.spy.foo, called().with_args(anything()))

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

    # issue 9
    def test_ANY_ARG_forbbiden_as_keyword_value(self):
        person = Spy()
        person.set_info(name="John", surname="Doe")

        assert_that(person.set_info,
                    called().with_args(name=anything(), surname="Doe"))

        with self.assertRaises(WrongApiUsage):
            assert_that(person.set_info,
                        called().with_args(name=ANY_ARG, surname="Doe"))

    def test_ANY_ARG_must_be_last_positional_argument(self):
        self.spy.method(1, 2, 3)

        with self.assertRaises(WrongApiUsage):
            assert_that(self.spy.method,
                        called().with_args(1, ANY_ARG, 3))

    def test_ANY_ARG_must_be_last_positional_argument_with_xarg(self):
        self.spy.method(1, 2, 3, name='Bob')

        with self.assertRaises(WrongApiUsage):
            assert_that(self.spy.method,
                        called().with_args(1, ANY_ARG, name='Bob'))

    def test_ANY_ARG_must_be_last_positional_argument__restricted_spy(self):
        spy = Spy(Collaborator)

        with self.assertRaises(WrongApiUsage):
            assert_that(spy.two_args_method,
                        called().with_args(ANY_ARG, 2))

        with self.assertRaises(WrongApiUsage):
            assert_that(spy.three_args_method,
                        called().with_args(1, ANY_ARG, 3))


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

    # doc FIXME: assure this is tested with doctests and remove
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
        assert_that(self.spy.foo, called().with_args(ANY_ARG).times(4))          # = 4
        assert_that(self.spy.foo, called().with_args(1).times(2))                # = 2
        assert_that(self.spy.foo, called().with_args(1).times(greater_than(1)))  # > 1
        assert_that(self.spy.foo, called().with_args(1).times(less_than(5)))     # < 5

    # doc FIXME: assure this is tested with doctests and remove
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

    # new on 1.7
    def test_assert_that_requires_a_matcher(self):
        self.assertRaises(MatcherRequiredError, assert_that, self.spy.m1, True)

    # from pydoubles docs
    def test_has_entry_matcher(self):
        with Spy() as spy:
            spy.one_arg_method(has_entry(is_('two'), 2)).returns(1000)

        assert_that(spy.one_arg_method({'one': 1, 'two': 2}), is_(1000))

    def test_all_of_matcher(self):
        with Spy() as spy:
            spy.one_arg_method(all_of(starts_with('h'), instance_of(str))).returns(1000)
        assert_that(spy.one_arg_method('hello'), is_(1000))


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
            self.stub.foo().delegates(list(range(3)))

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
            self.fail("Exception should be raised")

        except WrongApiUsage as e:
            expected = "delegates() must be called with callable or iterable instance (got 'None' instead)"
            assert_that(str(e), contains_string(expected))

    # FIXME: explain in docs
    def test_delegates_with_params(self):
        with self.stub:
            self.stub.foo(anything()).delegates(lambda x: x + 2)

        assert_that(self.stub.foo(3), is_(5))

    # new on 1.8.2
    # FIXME: include in docs
    def test_delegate_to_dict(self):
        with self.stub:
            self.stub.foo(anything()).delegates({0: 2, 1: 7, 2: 12})

        assert_that(self.stub.foo(1), is_(7))


class MockDelegateTest(TestCase):
    def setUp(self):
        self.mock = Mock()

    def assert_012(self, method):
        for x in range(3):
            assert_that(method(), is_(x))

    def test_delegate_to_list_is_only_an_expectation(self):
        with self.mock:
            self.mock.foo().delegates(list(range(3)))

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
            assert_that(spy, instance_of(cls))

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

    def test_spy_get_property_using_class(self):
        spy = Spy(ObjCollaborator)
        skip = spy.prop
        assert_that(spy, property_got('prop'))

    def test_spy_get_property_using_instance(self):
        spy = Spy(ObjCollaborator())
        skip = spy.prop
        assert_that(spy, property_got('prop'))

    def test_spy_not_get_property(self):
        spy = Spy(ObjCollaborator)
        assert_that(spy, never(property_got('prop')))

    def test_spy_get_property_fail(self):
        spy = Spy(ObjCollaborator)

        with self.assertRaises(AssertionError):
            assert_that(spy, property_got('prop'))

    def test_spy_set_property_using_class(self):
        spy = Spy(ObjCollaborator)
        spy.prop = 2
        assert_that(spy, property_set('prop'))

    def test_spy_set_property_using_instance(self):
        spy = Spy(ObjCollaborator())
        spy.prop = 2
        assert_that(spy, property_set('prop'))

    def test_spy_not_set_property(self):
        spy = Spy(ObjCollaborator)
        assert_that(spy, never(property_set('prop')))

    def test_spy_set_property_fail(self):
        spy = Spy(ObjCollaborator)

        with self.assertRaises(AssertionError):
            assert_that(spy, property_set('prop'))

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
        assert_that(spy,
                    property_set('prop').to(greater_than(1)).
                    times(less_than(3)))

    def test_proxyspy_get_actual_property(self):
        collaborator = ObjCollaborator()
        sut = ProxySpy(collaborator)
        assert_that(sut.prop, is_(1))

    def test_proxyspy_get_stubbed_property(self):
        collaborator = ObjCollaborator()
        with ProxySpy(collaborator) as sut:
            sut.prop = 2
        assert_that(sut.prop, is_(2))

    def test_proxyspy_set_property(self):
        collaborator = ObjCollaborator()
        sut = ProxySpy(collaborator)
        sut.prop = 20
        assert_that(sut.prop, is_(20))
        assert_that(collaborator.prop, is_(20))


# new on 1.8
class PropertyMockTests(TestCase):
    def test_mock_get(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop

        mock.prop

        assert_that(mock, verify())

    def test_mock_get_but_never_got(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop

        with self.assertRaises(AssertionError):
            assert_that(mock, verify())

    def test_mock_get_too_many_times(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop

        mock.prop
        mock.prop

        with self.assertRaises(AssertionError):
            assert_that(mock, verify())

    def test_mock_set(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop = 5

        mock.prop = 5

        assert_that(mock, verify())

    def test_mock_set_but_never_set(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop = 5

        with self.assertRaises(AssertionError):
            assert_that(mock, verify())

    def test_mock_set_too_many_times(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop = 5

        mock.prop = 5
        mock.prop = 5

        with self.assertRaises(AssertionError):
            assert_that(mock, verify())

    def test_mock_set_wrong_value(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop = 5

        with self.assertRaises(AssertionError):
            mock.prop = 8

    def test_mock_set_anything(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop = anything()

        mock.prop = 5

        assert_that(mock, verify())

    def test_mock_set_matcher(self):
        with Mock(ObjCollaborator) as mock:
            mock.prop = all_of(greater_than(8), less_than(12))

        mock.prop = 10

        assert_that(mock, verify())


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
        barrier.wait(1)  # test probably FAILS without this

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

    def test_spy_async_support_1_call_only(self):
        # given
        spy = Spy()
        sut = AsyncTests.SUT(spy)

        # when
        sut.send_data(3)
        sut.send_data(3)

        # then
        with self.assertRaises(WrongApiUsage):
            assert_that(spy.write, called().async(timeout=1).with_args(3).times(2))

    def test_spy_async_stubbed(self):
        # given
        with Spy() as spy:
            spy.write(ANY_ARG).returns(100)

        sut = AsyncTests.SUT(spy)

        # when
        sut.send_data(3)

        # then
        assert_that(spy.write, called().async(timeout=1))


# new on 1.7
class with_some_args_matcher_tests(TestCase):
    def test_one_arg(self):
        spy = Spy(Collaborator)
        spy.mixed_method(5)
        assert_that(spy.mixed_method, called().with_args(5))
        assert_that(spy.mixed_method, called().with_args(arg1=5))

    def test_two_arg(self):
        spy = Spy(Collaborator)
        spy.two_args_method(5, 10)
        assert_that(spy.two_args_method, called().with_args(5, 10))
        assert_that(spy.two_args_method, called().with_args(arg1=5, arg2=10))
        assert_that(spy.two_args_method, called().with_some_args(arg1=5))
        assert_that(spy.two_args_method, called().with_some_args(arg2=10))
        assert_that(spy.two_args_method, called().with_some_args())

    def test_free_spy(self):
        spy = Spy()
        spy.foo(1, 3)

        with self.assertRaises(WrongApiUsage):
            assert_that(spy.foo, called().with_some_args())


# new on 1.7
class Stub_default_behavior_tests(TestCase):
    def test_set_return_globally(self):
        StubClone = Stub._clone_class()
        set_default_behavior(StubClone, method_returning(20))
        stub = StubClone()

        assert_that(stub.unknown(), is_(20))

    def test_set_exception_globally(self):
        StubClone = Stub._clone_class()
        set_default_behavior(StubClone, method_raising(SomeException))
        stub = StubClone()

        with self.assertRaises(SomeException):
            stub.unknown()

    def test_set_return_by_instance(self):
        stub = Stub()
        set_default_behavior(stub, method_returning(20))

        assert_that(stub.unknown(), is_(20))

    def test_set_exception_by_instance(self):
        stub = Stub()
        set_default_behavior(stub, method_raising(SomeException))

        with self.assertRaises(SomeException):
            stub.unknown()

    def test_restricted_stub(self):
        stub = Stub(Collaborator)
        set_default_behavior(stub, method_returning(30))
        with stub:
            stub.hello().returns(1000)

        assert_that(stub.something(), is_(30))
        assert_that(stub.hello(), is_(1000))


# new on 1.7
class Spy_default_behavior_tests(TestCase):
    def test_set_return_globally(self):
        SpyClone = Spy._clone_class()
        set_default_behavior(SpyClone, method_returning(20))
        spy = SpyClone()

        assert_that(spy.unknown(7), is_(20))

        assert_that(spy.unknown, called().with_args(7))
        assert_that(spy.unknown, never(called().with_args(9)))

    def test_set_return_by_instance(self):
        spy = Spy()
        set_default_behavior(spy, method_returning(20))

        assert_that(spy.unknown(7), is_(20))

        assert_that(spy.unknown, called().with_args(7))


# new on 1.7
class ProxySpy_default_behavior_tests(TestCase):
    def test_this_change_proxyspy_default_behavior(self):
        spy = ProxySpy(Collaborator())
        assert_that(spy.hello(), is_("hello"))

        set_default_behavior(spy, method_returning(40))
        assert_that(spy.hello(), is_(40))


class orphan_spy_method_tests(TestCase):
    # new on 1.8.2
    # issue 21
    def test_spy(self):
        m = method_returning(3)
        m()
        assert_that(m, called())


# FIXME: new on tip
class new_style_orphan_methods_tests(TestCase):
    def setUp(self):
        self.obj = Collaborator()

    def test_stub_method(self):
        with Stub() as stub:
            stub.method(1).returns(100)
            stub.method(2).returns(200)

        self.obj.foo = stub.method

        assert_that(self.obj.foo(0), is_(None))
        assert_that(self.obj.foo(1), is_(100))
        assert_that(self.obj.foo(2), is_(200))

    def test_spy_method(self):
        with Spy() as spy:
            spy.method(1).returns(100)
            spy.method(2).returns(200)
            spy.method(3).raises(SomeException)

        self.obj.foo = spy.method

        assert_that(self.obj.foo(0), is_(None))
        assert_that(self.obj.foo(1), is_(100))
        assert_that(self.obj.foo(2), is_(200))
        with self.assertRaises(SomeException):
            self.obj.foo(3)

        assert_that(self.obj.foo, called().times(4))
        assert_that(spy.method, called().times(4))

#    def test_spy_method__brief_method(self):
#        with method() as self.obj.foo:
#            self.obj.foo().returns(100)
#            self.obj.foo(2).returns(200)
#
#        assert_that(self.obj.foo(), is_(100))
#        assert_that(self.obj.foo(2), is_(200))
#        assert_that(self.obj.foo(3), is_(None))
#
#        assert_that(self.obj.foo, called().times(3))
#        assert_that(spy.method, called().times(3))


class custom_types_tests(TestCase):
    # issue 22
    def test_custom_equality_comparable_objects(self):
        class A(object):
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                return self.value == other.value

        with Stub() as stub:
            stub.foo(A(1)).returns(A(1))

        self.assertEquals(A(1), stub.foo(A(1)))


class when_tests(TestCase):
    def test_stub_when(self):
        stub = Stub()
        when(stub).add(2, 2).returns(5)
        when(stub).add(2, 4).returns(8)
        when(stub).sub(3, ANY_ARG).returns(100)
        when(stub).foo(ANY_ARG).returns_input()
        when(stub).foo(anything(), 7).returns(300)

        assert_that(stub.add(2, 2), is_(5))
        assert_that(stub.add(2, 4), is_(8))
        assert_that(stub.sub(3, 600), is_(100))
        assert_that(stub.foo((8, 2)), is_((8, 2)))
        assert_that(stub.foo(3, 7), is_(300))

        assert_that(stub.add(), is_(None))

    def test_stub_when_with_args(self):
        stub = Stub()
        when(stub).some_calculation(5).returns(10)
        when(stub).some_calculation(10).returns(20)

        assert_that(stub.some_calculation(5), is_(10))

    def test_spy_when(self):
        spy = Spy()
        when(spy).add(2, 2).returns(5)
        when(spy).add(2, 4).returns(8)

        assert_that(spy.add(2, 2), is_(5))
        assert_that(spy.add(2, 4), is_(8))
        assert_that(spy.add(), is_(None))

    # from pydoubles docs
    def test_has_entry_matcher(self):
        spy = Spy()
        when(spy).one_arg_method(has_entry(is_('two'), 2)).returns(1000)
        assert_that(spy.one_arg_method({'one': 1, 'two': 2}), is_(1000))

    def test_all_of_matcher(self):
        spy = Spy()
        when(spy).one_arg_method(all_of(starts_with('h'), instance_of(str))).returns(1000)
        assert_that(spy.one_arg_method('hello'), is_(1000))


class expect_call_tests(TestCase):
    def test_expect_call(self):
        mock = Mock()
        expect_call(mock).add(2, 4)
        expect_call(mock).add(2, 2).returns(5)

        mock.add(2, 4)
        assert_that(mock.add(2, 2), is_(5))

        assert_that(mock, verify())

    def test_except_call_with_stub_or_spy_forbidden(self):
        with self.assertRaises(WrongApiUsage):
            expect_call(Stub()).foo()

        with self.assertRaises(WrongApiUsage):
            expect_call(Spy()).foo()


# new on 1.7.2
class VarArgsTest(TestCase):
    def test_stub_args(self):
        stub = Stub(Collaborator)
        with stub:
            stub.varargs(1).returns(10)
            stub.varargs(1, 2).returns(200)
            stub.varargs(1, 3, ANY_ARG).returns(300)
            stub.varargs(2, anything()).returns(400)

        assert_that(stub.varargs(42), is_(None))
        assert_that(stub.varargs(1), is_(10))

        assert_that(stub.varargs(1, 2), is_(200))
        assert_that(stub.varargs(1, 2, 7), is_(None))

        assert_that(stub.varargs(1, 3), is_(300))
        assert_that(stub.varargs(1, 3, 7), is_(300))

        assert_that(stub.varargs(1, 5), is_(None))

        assert_that(stub.varargs(2), is_(None))
        assert_that(stub.varargs(2, 3), is_(400))
        assert_that(stub.varargs(2, 3, 4), is_(None))

    def test_spy_args(self):
        spy = Spy(Collaborator)
        spy.varargs(1, 2, 3)

        assert_that(spy.varargs, called())
        assert_that(spy.varargs, called().with_args(1, 2, 3))
        assert_that(spy.varargs, called().with_args(1, ANY_ARG))

    def test_spy_kargs(self):
        spy = Spy(Collaborator)
        spy.varargs(one=1, two=2)

        assert_that(spy.varargs, called())
        assert_that(spy.varargs, called().with_args(one=1, two=2))
        assert_that(spy.varargs, called().with_args(one=1, two=anything()))

    def test_with_some_args_is_not_applicable(self):
        spy = Spy(Collaborator)
        spy.varargs(one=1, two=2)

        try:
            assert_that(spy.varargs, called().with_some_args(one=1))
            self.fail('exception should be raised')
        except WrongApiUsage as e:
            assert_that(str(e),
                        contains_string('with_some_args() can not be applied to method Collaborator.varargs(self, *args, **kargs)'))


# new on 1.7.2
class TracerTests(TestCase):
    def setUp(self):
        self.out = StringIO()
        self.tracer = Tracer(self.out.write)

    def test_trace_single_method(self):
        with Stub() as stub:
            stub.foo(ANY_ARG).returns(1)

        self.tracer.trace(stub.foo)

        stub.foo(1, two=2)

        assert_that(self.out.getvalue(), is_("Stub.foo(1, two=2)"))

    def test_trace_single_non_stubbed_method(self):
        stub = Stub()
        self.tracer.trace(stub.non)

        stub.non(1, "two")

        assert_that(self.out.getvalue(), is_("Stub.non(1, 'two')"))

    def test_trace_all_double_INSTANCE_methods(self):
        stub = Stub()
        self.tracer.trace(stub)

        stub.bar(2, "three")

        assert_that(self.out.getvalue(), is_("Stub.bar(2, 'three')"))

    def test_trace_all_double_CLASS_methods(self):
        self.tracer.trace(Stub)
        stub = Stub()

        stub.fuzz(3, "four")

        assert_that(self.out.getvalue(), is_("Stub.fuzz(3, 'four')"))

    def test_trace_get_property(self):
        stub = Stub(ObjCollaborator)
        self.tracer.trace(stub)

        stub.prop

        assert_that(self.out.getvalue(),
                    is_("ObjCollaborator.prop gotten"))

    def test_trace_set_property(self):
        stub = Stub(ObjCollaborator)
        self.tracer.trace(stub)

        stub.prop = 2

        assert_that(self.out.getvalue(),
                    is_("ObjCollaborator.prop set to 2"))


class SomeException(Exception):
    pass


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


class Collaborator:
    """
    The original object we double in tests
    """
    class_attr = "OK"

    def __init__(self):
        self.instance_attr = 300

    def hello(self):
        return "hello"

    def something(self):
        return "ok"

    def one_arg_method(self, arg1):
        return arg1

    def two_args_method(self, arg1, arg2):
        return arg1 + arg2

    def three_args_method(self, arg1, arg2, arg3):
        return arg1 + arg2 + arg3

    def kwarg_method(self, key_param=False):
        return key_param

    def mixed_method(self, arg1, key_param=False):
        return key_param + arg1

    def void_method(self):
        pass

    def method_one(self, arg1):
        return 1

    def varargs(self, *args, **kargs):
        return len(args)

    alias_method = one_arg_method
