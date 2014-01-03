Inline stubbing and mocking
===========================

.. versionadded:: 1.8 - Proposed by `Carlos Ble <https://bitbucket.org/carlosble>`_

Several pyDoubles users ask for an alternative to set stubbing and mocking in a way
similar to pyDoubles API, that is, instead of use the double context manager:

.. sourcecode:: python

   with Stub() as stub:
       stub.foo(1).returns(100)

   with Mock() as mock:
       mock.bar(2).returns(50)

You may invoke the :py:func:`when` and :py:func:`except_call` functions to get the same
setup.

.. sourcecode:: python

   stub = Stub()
   when(stub).foo(1).returns(100)

   mock = Mock()
   expect_call(mock).bar(2).returns(50)


Note that :py:func:`when` and :py:func:`except_call` internally provide almost the same
functionality. Two functions are provide only for test readability
purposes. :py:func:`when` is intented for stubs, spies and proxyspies, and
:py:func:`except_call` is intented for mocks.


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-column: 90
.. End:
