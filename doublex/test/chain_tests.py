# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase
import doublex


class ChainTests(TestCase):
    def test_chain_default_behavior(self):
        stub = doublex.Stub()

        doublex.set_default_behavior(stub, doublex.Spy)
        chained_spy = stub.foo()
        chained_spy.bar()

        doublex.assert_that(chained_spy.bar, doublex.called())
