=========
Reference
=========


.. index::
   single:  assert_that()

.. _sec assert_that:

assert_that()
=============

`assert()`__ evaluates a boolean expression, but ``assert_that()`` takes an arbitrary
object and a `matcher`__, that is applied over the former. This way makes possible to
build up complex assertions by means of matcher composition.

__ http://docs.python.org/2/reference/simple_stmts.html#the-assert-statement
__ http://pythonhosted.org/PyHamcrest/tutorial.html


CAUTION: Be ware about ``hamcrest.assert_that()``
-------------------------------------------------

Note the `hamcrest.assert_that()`__
function has two different behavior depending of its arguments:

__ https://github.com/hamcrest/PyHamcrest/blob/master/hamcrest/core/assert_that.py#L39

* ``assert_that(actual, matcher, [reason])``
  In this form the ``matcher`` is applied to the ``actual`` object. If the
  matcher fails, it raises AssertionError showing the optional reason.

* ``assert_that(value, [reason])``
  If the boolean interpretation of ``value`` is False, it raises
  AssertionError showing the optional reason.

It implies that something like:

.. sourcecode:: python

   from hamcrest import assert_that

   assert_that(foo, bar)


If ``bar`` is not a matcher, the assertion is satisfied for any non-false ``foo``,
independently of the value of ``bar``. A more obvious example:

.. sourcecode:: python

   from hamcrest import assert_that

   assert_that(2 + 2, 5)  # OMG! that assertion IS satisfied!

For this reason, when you need compare values (equivalent to the unit ``assertEquals``) you must always use a matcher, like ``is_`` or ``equal_to``:

.. sourcecode:: python

   assert_that(2 + 2, is_(5))       # that assertion is NOT satisfied!
   assert_that(2 + 2, equal_to(5))  # that assertion is NOT satisfied!


.. index::
   single:  assert_that()


Prefer ``doublex.assert_that``
------------------------------

.. versionadded:: 1.7 - (thanks to `Eduardo Ferro`__)

__ https://bitbucket.org/DavidVilla/python-doublex/pull-request/5/assert_that-raises


To avoid the issues described in the previous section, doublex provides an alternative
``assert_that()`` implementation that enforces a matcher as second argument.


.. sourcecode:: python

   >>> from doublex import assert_that
   >>> assert_that(1, 1)
   Traceback (most recent call last):
   ...
   MatcherRequiredError: 1 should be a hamcrest Matcher


.. index::
   single:  Stub

Stubbing
========

The stub provides all methods in the collaborator interface. When the collaborator is not
given (a free stub), the stub seems to have any method you invoke on it. The default
behavior for non stubbed methods is to return ``None``, although it can be changed (see :ref:`set_default_behavior`).


.. sourcecode:: python

   >>> from doublex import Stub
   >>> stub = Stub()
   >>> stub.method()

This behavior may be customized in each test using the Python context manager facility:

.. sourcecode:: python

   from doublex import Stub

   with Stub() as stub:
    	stub.method(<args>).returns(<value>)


`Hamcrest <https://code.google.com/p/hamcrest/wiki/TutorialPython>`_ matchers may be used
to define amazing stub conditions:


.. sourcecode:: python

   from hamcrest import all_of, has_length, greater_than, less_than
   from doublex import Stub, assert_that, is_

   with Stub() as stub:
       stub.foo(has_length(less_than(4))).returns('<4')
       stub.foo(has_length(4)).returns('four')
       stub.foo(has_length(
   		all_of(greater_than(4),
                       less_than(8)))).returns('4<x<8')
       stub.foo(has_length(greater_than(8))).returns('>8')

   assert_that(stub.foo((1, 2)), is_('<4'))
   assert_that(stub.foo('abcd'), is_('four'))
   assert_that(stub.foo('abcde'), is_('4<x<8'))
   assert_that(stub.foo([0] * 9), is_('>8'))


.. _returns_input:

Stubs returning input
---------------------


.. sourcecode:: python

   from doublex import Stub, assert_that

   def test_returns_input(self):
       with Stub() as stub:
           stub.foo(1).returns_input()

       assert_that(stub.foo(1), is_(1))


.. _raises:

Stubs raising exceptions
------------------------


.. sourcecode:: python

   from doublex import Stub

   def test_raises(self):
       with Stub() as stub:
           stub.foo(2).raises(SomeException)

       with self.assertRaises(SomeException):
           stub.foo(2)


.. _set_default_behavior:

Changing default stub behavior
------------------------------

.. versionadded:: 1.7 - (thanks to `Eduardo Ferro`__)

__ https://bitbucket.org/DavidVilla/python-doublex/pull-request/4/stub-configuration-for-raise-an-error-when


Any non-stubbed method returns ``None``. But this behavior can be changed by means of ``set_default_behavior()`` function. It can be applied to any double class: ``Stub``, ``Spy``, ``ProxySpy`` or ``Mock``.

.. sourcecode:: python

   from doublex import Stub, assert_that
   from doublex import set_default_behavior, method_returning

   set_default_behavior(Stub, method_returning(20))
   stub  = Stub()
   assert_that(stub.unknown(), is_(20))

Or to a specific instance:


.. sourcecode:: python

   from doublex import Stub, assert_that, is_
   from doublex import set_default_behavior, method_returning

   stub = Stub()
   set_default_behavior(stub, method_returning(20))
   assert_that(stub.unknown(), is_(20))

Also, it is possible to raise some exception:


.. sourcecode:: python

   >>> from doublex import Stub, set_default_behavior, method_raising
   >>> stub = Stub()
   >>> set_default_behavior(stub, method_raising(SomeException))
   >>> stub.unknown()
   Traceback (most recent call last):
   ...
   SomeException


Asserting method calls
======================

To assert method invocations you need a ``Spy`` and the ``called()`` matcher.

.. index::
   single:  called()

.. _called:

called()
--------

``called()`` matches method invocation (argument values are not relevant):


.. sourcecode:: python

   from doublex import Spy, assert_that, called

   spy = Spy()

   spy.m1()
   spy.m2(None)
   spy.m3("hi", 3.0)
   spy.m4([1, 2])

   assert_that(spy.m1, called())
   assert_that(spy.m2, called())
   assert_that(spy.m3, called())
   assert_that(spy.m4, called())


.. index::
   single: with_args()

.. _with_args:

with_args(): asserting calling argument values
----------------------------------------------

Match explicit argument values:


.. sourcecode:: python

   from hamcrest import contains_string, less_than, greater_than
   from doublex import Spy, assert_that, called

   spy = Spy()

   spy.m1()
   spy.m2(None)
   spy.m3(2)
   spy.m4("hi", 3.0)
   spy.m5([1, 2])
   spy.m6(name="john doe")

   assert_that(spy.m1, called())
   assert_that(spy.m2, called())

   assert_that(spy.m1, called().with_args())
   assert_that(spy.m2, called().with_args(None))
   assert_that(spy.m3, called().with_args(2))
   assert_that(spy.m4, called().with_args("hi", 3.0))
   assert_that(spy.m5, called().with_args([1, 2]))
   assert_that(spy.m6, called().with_args(name="john doe"))


Remember that `hamcrest matchers
<https://code.google.com/p/hamcrest/wiki/TutorialPython>`_ matchers
are fully supported:


.. sourcecode:: python

   assert_that(spy.m3, called().with_args(less_than(3)))
   assert_that(spy.m3, called().with_args(greater_than(1)))
   assert_that(spy.m6, called().with_args(name=contains_string("doe")))


Other example with a string argument and combining several matchers:


.. sourcecode:: python

   from hamcrest import has_length, greater_than, less_than
   from doublex import Spy, assert_that, called, never

   spy = Spy()

   spy.foo("abcd")

   assert_that(spy.foo, called().with_args(has_length(4)))
   assert_that(spy.foo, called().with_args(has_length(greater_than(3))))
   assert_that(spy.foo, called().with_args(has_length(less_than(5))))
   assert_that(spy.foo, never(called().with_args(has_length(greater_than(5)))))


.. index::
   single:  hamcrest; anything()

anything(): asserting wildcard values
-------------------------------------

The ``anything()`` hamcrest matcher may be used to match any single value. That is useful when
only some arguments are relevant:


.. sourcecode:: python

   from hamcrest import anything

   spy.foo(1, 2, 20)
   spy.bar(1, key=2)

   assert_that(spy.foo, called().with_args(1, anything(), 20))
   assert_that(spy.bar, called().with_args(1, key=anything()))


.. index::
   single:  ANY_ARG

ANY_ARG: greedy argument value wildcard
---------------------------------------

``ANY_ARG`` is a special value that matches any subsequent argument values, including no
args. That is, ``ANY_ANG`` means "any value for any argument from here". If ``anything()``
is similar to the regular expression ``?``, ``ANY_ARG`` would be equivalent to ``*``.

For this reason, it has **no sense** to give other values or matchers after an
``ANY_ARG``. It is also applicable to keyword arguments due they have no order. In
summary, ``ANY_ARG``:

* it must be the last positional argument value.
* it can not be given as keyword value.
* it can not be given together keyword arguments.

Since version 1.7 a ``WrongAPI`` exception is raised if that situations (see
`issue 9 <https://bitbucket.org/DavidVilla/python-doublex/issue/9/called-with-named-params-and-any_arg-does>`_).

An example:


.. sourcecode:: python

   from doublex import ANY_ARG

   spy.arg0()
   spy.arg1(1)
   spy.arg3(1, 2, 3)
   spy.arg_karg(1, key1='a')

   assert_that(spy.arg0, called())
   assert_that(spy.arg0, called().with_args(ANY_ARG))  # equivalent to previous

   assert_that(spy.arg1, called())
   assert_that(spy.arg1, called().with_args(ANY_ARG))  # equivalent to previous

   assert_that(spy.arg3, called().with_args(1, ANY_ARG))
   assert_that(spy.arg_karg, called().with_args(1, ANY_ARG))


Also for stubs:


.. sourcecode:: python

   from doublex import Stub, assert_that, ANY_ARG, is_

   with Stub() as stub:
       stub.foo(ANY_ARG).returns(True)
       stub.bar(1, ANY_ARG).returns(True)

   assert_that(stub.foo(), is_(True))
   assert_that(stub.foo(1), is_(True))
   assert_that(stub.foo(key1='a'), is_(True))
   assert_that(stub.foo(1, 2, 3, key1='a', key2='b'), is_(True))

   assert_that(stub.foo(1, 2, 3), is_(True))
   assert_that(stub.foo(1, key1='a'), is_(True))


.. index::
   single:  with_some_args()

.. _with_some_args:

with_some_args(): asserting just relevant arguments
---------------------------------------------------

.. versionadded:: 1.7

When a method has several arguments and you need to assert an invocation giving a specific
value just for some of them, you may use the :py:func:`anything` matcher for the rest of
them. That works but the resulting code is a bit dirty:


.. sourcecode:: python

   from hamcrest import anything
   from doublex import Spy, assert_that, ANY_ARG

   class Foo:
       def five_args_method(self, a, b, c, d, e=None):
           return 4

   spy = Spy(Foo)
   spy.five_args_method(1, 2, 'bob', 4)

   # only the 'c' argument is important in the test
   assert_that(spy.five_args_method,
               called().with_args(anything(), anything(), 'bob', anything()))
   # assert only 'b' argument
   assert_that(spy.five_args_method,
               called().with_args(anything(), 2, ANY_ARG))


The :py:func:`with_some_args()` allows to specify just some arguments, assuming all other can take any value. The same example using :py:func:`with_some_arg()`:


.. sourcecode:: python

   from doublex import Spy, assert_that, called

   class Foo:
       def five_args_method(self, a, b, c, d, e=None):
           return 4

   spy = Spy(Foo)
   spy.five_args_method(1, 2, 'bob', 4)

   # only the 'c' argument is important in the test
   assert_that(spy.five_args_method,
               called().with_some_args(c='bob'))
   # assert only 'b' argument
   assert_that(spy.five_args_method,
               called().with_some_args(b=2))


This method may be used with both keyword and non-keyword arguments.

.. warning::
   Formal argument name is mandatory, so this is only applicable to restricted spies
   (those that are instantiated giving a collaborator).


.. index::
   single:  never()

.. _never:

never()
-------

Convenient replacement for ``hamcrest.is_not()``:


.. sourcecode:: python

   from hamcrest import is_not
   from doublex import Spy, assert_that, called, never

   spy = Spy()

   assert_that(spy.m5, is_not(called()))  # is_not() works
   assert_that(spy.m5, never(called()))   # but prefer never() due to better error report messages


.. index::
   single:  times()

.. _times:

times(): asserting number of calls
----------------------------------


.. sourcecode:: python

   from hamcrest import anything, all_of, greater_than, less_than
   from doublex import Spy, assert_that, called, ANY_ARG, never

   spy = Spy()

   spy.foo()
   spy.foo(1)
   spy.foo(1)
   spy.foo(2)

   assert_that(spy.unknown, never(called()))                    # = 0 times
   assert_that(spy.foo, called())                               # > 0
   assert_that(spy.foo, called().times(greater_than(0)))        # > 0 (same)
   assert_that(spy.foo, called().times(4))                      # = 4
   assert_that(spy.foo, called().times(greater_than(2)))        # > 2
   assert_that(spy.foo, called().times(less_than(6)))           # < 6

   assert_that(spy.foo, never(called().with_args(5)))                  # = 0 times
   assert_that(spy.foo, called().with_args().times(1))                 # = 1
   assert_that(spy.foo, called().with_args(anything()))                # > 0
   assert_that(spy.foo, called().with_args(ANY_ARG).times(4))          # = 4
   assert_that(spy.foo, called().with_args(1).times(2))                # = 2
   assert_that(spy.foo, called().with_args(1).times(greater_than(1)))  # > 1
   assert_that(spy.foo, called().with_args(1).times(less_than(5)))     # < 5
   assert_that(spy.foo, called().with_args(1).times(
               all_of(greater_than(1), less_than(8))))                 # 1 < times < 8


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
