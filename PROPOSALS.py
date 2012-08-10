#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase

from hamcrest import *
from pydoubles2 import Spy, Mock, called, called_with, \
    assert_expectations, ANY_ARG


DESIGN_PRINCIPLES = '''
- Doubles have not framework specific methods. It avoid silent misspelling.
- It is not required to instantiate collaborators
- hamcrest.assert_that used for all assertions
- Invocation order is required by default
'''


class StubWishes(TestCase):
    def test_programming_a_stub_invoking_it(self):
        with Stub() as stub:
            stub.foo('hi').returns(10)
            stub.hello(ANY_ARG).returns(False)
            stub.bye().raises(SomeException)

        assert_that(stub.foo(), 10)


class SpyWishes(TestCase):
    def test_hamcrest_assertions(self):
        sender = Spy()  # empty spy

        sender.send_mail('hi')

        assert_that(sender.send_mail, called())
        assert_that(sender.send_mail, called().times(2))
        assert_that(sender.send_mail, called_with('foo@bar.net'))
_
        # these may be just aliases for hamcrest.is_not (sintactic molasses)
        assert_that(sender.close, was_not(called()))
        assert_that(sender.close, never(called()))

    def test_checking_interface(self):
        sender = Spy(Sender)  # arg may be a class (instance is not required)

    def test_proxy_as_config(self):
        sender = ProxySpy(Sender())


class MockWishes(TestCase):
    def test_programming_a_mock_invoking_it(self):
        sender = Mock()
        with sender:
            sender.send_mail()  # inoked without args
            sender.send_mail(ANY_ARG)  # any invocation
            sender.send_mail('wrong_mail').returns(FAILURE)
            sender.send_mail_exc('wrong_mail').raises(WrongMailException)

        mock.foo('bye')

        assert_that(mock, meets_expectations())

    def test_lossy_invocation_order(self):
        sender = SmoothMock()
        with sender:
            sender.send_mail('FOO@cat.net')
            sender.send_mail('bar@example.net')

        sender.send_mail('bar@example.net')
        sender.send_mail('FOO@cat.net')

        assert_that(mock, meets_expectations())

    def test_checking_interface(self):
        sender = Mock(Sender)  # arg may be a class (instance is not required)


# Future features:
# - classmethod
# - staticmethod
# - property
