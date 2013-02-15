# -*- mode: python; coding: utf-8 -*-

# All bugs by Oscar Aceña <oscar.acena@gmail.com>

import time
import thread
import unittest

from doublex import ProxySpy, assert_that, called


class Collaborator(object):
    def write(self, data):
        time.sleep(0.3)


class SUT(object):
    def __init__(self, collaborator):
        self.collaborator = collaborator

    def delayed_write(self):
        time.sleep(0.1)
        self.collaborator.write("something")

    def some_method(self):
        thread.start_new_thread(self.delayed_write, ())


class AsyncTests(unittest.TestCase):
    def test_wrong_try_to_test_an_async_invocation(self):
        # given
        spy = ProxySpy(Collaborator())
        sut = SUT(spy)

        # when
        sut.some_method()

        # then
        assert_that(spy.write, called().async(1))
