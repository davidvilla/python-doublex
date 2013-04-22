#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase
from doublex import (Stub, Spy, ProxySpy, Mock,
                     assert_that, called, ANY_ARG, never,
                     verify, any_order_verify)
from hamcrest import greater_than, anything, contains_string


class AlreadyExists(Exception):
    pass


class InvalidPassword(Exception):
    pass


class AccountStore:
    def save(self, login, password):
        pass

    def has_user(self, login):
        pass


class PasswordService:
    def generate(self):
        pass


class AccountService:
    def __init__(self, store, password_service):
        self.store = store
        self.password_service = password_service

    def create(self, login):
        if self.store.has_user(login):
            raise AlreadyExists()

        password = self.password_service.generate()
        if not password:
            raise InvalidPassword()

        self.store.save(login, password)


class AccountTests(TestCase):
    def test_account_creation__free_stub(self):
        with Stub() as password_service:
            password_service.generate().returns('some')

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')

        assert_that(store.save, called())

    def test_account_creation__restricted_stub(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().returns('some')

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')

        assert_that(store.save, called())

    def test_account_creation__3_accounts(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().returns('some')

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')
        service.create('Peter')
        service.create('Alice')

        assert_that(store.save, called().times(3))
        assert_that(store.save, called().times(greater_than(2)))

    def test_account_creation__argument_values(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().returns('some')

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')

        assert_that(store.save, called().with_args('John', 'some'))
        assert_that(store.save, called().with_args('John', ANY_ARG))
        assert_that(store.save, never(called().with_args('Alice', anything())))
        assert_that(store.save,
                    called().with_args(contains_string('oh'), ANY_ARG))

    def test_account_creation__report_message(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().returns('some')

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')
        service.create('Alice')

        # assert_that(store.save, called().with_args('Peter'))

    def test_account_already_exists(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().returns('some')

        with ProxySpy(AccountStore()) as store:
            store.has_user('John').returns(True)

        service = AccountService(store, password_service)

        with self.assertRaises(AlreadyExists):
            service.create('John')

    def test_account_behaviour_with_mock(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().returns('some')

        with Mock(AccountStore) as store:
            store.has_user('John')
            store.save('John', 'some')
            store.has_user('Peter')
            store.save('Peter', 'some')

        service = AccountService(store, password_service)

        service.create('John')
        service.create('Peter')

        assert_that(store, verify())

#    def test_account_behaviour_with_mock_any_order(self):
#        with Stub(PasswordService) as password_service:
#            password_service.generate().returns('some')
#
#        with Mock(AccountStore) as store:
#            store.has_user('John')
#            store.has_user('Peter')
#            store.save('John', 'some')
#            store.save('Peter', 'some')
#
#        service = AccountService(store, password_service)
#
#        service.create('John')
#        service.create('Peter')
#
#        assert_that(store, any_order_verify())

    def test_stub_delegates(self):
        def get_pass():
            return "12345"

        with Stub(PasswordService) as password_service:
            password_service.generate().delegates(get_pass)

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')

        assert_that(store.save, called().with_args('John', '12345'))

    def test_stub_delegates_list(self):
        with Stub(PasswordService) as password_service:
            password_service.generate().delegates(["12345", "mypass", "nothing"])

        store = Spy(AccountStore)
        service = AccountService(store, password_service)

        service.create('John')
        service.create('Peter')
        service.create('Alice')

        assert_that(store.save, called().with_args('John', '12345'))
        assert_that(store.save, called().with_args('Peter', 'mypass'))
        assert_that(store.save, called().with_args('Alice', 'nothing'))
