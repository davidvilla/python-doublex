=======
Doubles
=======

Some very basic examples are shown below. Remember that test doubles are created to be
invoked by your `SUT <http://en.wikipedia.org/wiki/System_under_test>`_, and a RealWorld™
test never directly invokes doubles.  Here we do it that way, but just for simplicity.

.. index::
   single: Stub

Stub
====

Hint: *Stubs tell you what you wanna hear.*

A ``Stub`` is a double object that may be programmed to return specified values depending on
method invocations and their arguments. You must use a context (the ``with`` keyword) for
that.

Invocations over the ``Stub`` must meet the collaborator interface:

.. testsetup:: *

   import unittest
   from doublex import Stub, Spy, ProxySpy, Mock, Mimic
   from doublex import ANY_ARG, assert_that, is_, never
   from doublex import called, verify, any_order_verify
   from doublex import method_returning, method_raising
   from doublex import property_got, property_set
   from doublex import set_default_behavior

   import hamcrest
   from hamcrest import contains_string, greater_than, has_length, less_than, all_of, anything

   class SomeException(Exception):
       pass

   class Collaborator(object):
       def hello(self):
           return "hello"

       def add(self, a, b):
           return a + b



.. sourcecode:: python

   class Collaborator:
       def hello(self):
           return "hello"

       def add(self, a, b):
           return a + b

   with Stub(Collaborator) as stub:
       stub.hello().raises(SomeException)
       stub.add(ANY_ARG).returns(4)

   assert_that(stub.add(2,3), is_(4))


If you call an nonexistent method you will get an ``AttributeError`` exception.


.. sourcecode:: python

   >>> with Stub(Collaborator) as stub:
   ...    stub.foo().returns(True)
   Traceback (most recent call last):
   ...
   AttributeError: 'Collaborator' object has no attribute 'foo'

Wrong argument number:


.. sourcecode:: python

   >>> with Stub(Collaborator) as stub:
   ...    stub.hello(1).returns(2)  # interface mismatch exception
   Traceback (most recent call last):
   ...
   TypeError: Collaborator.hello() takes exactly 1 argument (2 given)



"free" Stub
-----------

This allows you to invoke any method you want because it is not restricted to an interface.


.. sourcecode:: python

   # given
   with Stub() as stub:
       stub.foo('hi').returns(10)

   # when
   result = stub.foo('hi')

   # then
   assert_that(result, is_(10))


.. index::
   single: Spy

Spy
===

Hint: *Spies remember everything that happens to them.*

Spy extends the Stub functionality allowing you to assert on the invocation it receives since its creation.

Invocations over the Spy must meet the collaborator interface.


.. sourcecode:: python

   class Sender:
       def say(self):
           return "hi"

       def send_mail(self, address, force=True):
           pass  # [some amazing code]

   sender = Spy(Sender)

   sender.send_mail("john.doe@example.net")  # right, Sender.send_mail interface support this

   assert_that(sender.send_mail, called())
   assert_that(sender.send_mail, called().with_args("john.doe@example.net"))
   assert_that(sender.send_mail, called().with_args(contains_string("@example.net")))

   sender.bar()  # interface mismatch exception


.. sourcecode:: python

   Traceback (most recent call last):
   ...
   AttributeError: 'Sender' object has no attribute 'bar'



.. sourcecode:: python

   >>> sender = Spy(Sender)
   >>> sender.send_mail()
   Traceback (most recent call last):
   ...
   TypeError: Sender.send_mail() takes at least 2 arguments (1 given)


.. sourcecode:: python

   >>> sender = Spy(Sender)
   >>> sender.send_mail(wrong=1)
   Traceback (most recent call last):
   ...
   TypeError: Sender.send_mail() got an unexpected keyword argument 'wrong'


.. sourcecode:: python

   >>> sender = Spy(Sender)
   >>> sender.send_mail('foo', wrong=1)
   Traceback (most recent call last):
   ...
   TypeError: Sender.send_mail() got an unexpected keyword argument 'wrong'


"free" Spy
----------

As the "free" Stub, this is a spy not restricted by a collaborator interface.


.. sourcecode:: python

   # given
   with Spy() as sender:
       sender.helo().returns("OK")

   # when
   sender.send_mail('hi')
   sender.send_mail('foo@bar.net')

   # then
   assert_that(sender.helo(), is_("OK"))
   assert_that(sender.send_mail, called())
   assert_that(sender.send_mail, called().times(2))
   assert_that(sender.send_mail, called().with_args('foo@bar.net'))

.. index::
   single: ProxySpy

ProxySpy
--------

Hint: *Proxy spies forward invocations to its actual instance.*

The ``ProxySpy`` extends the ``Spy`` invoking the actual instance when the corresponding
spy method is called

.. warning::
   Note the ``ProxySpy`` breaks isolation. It is not really a double. Therefore is always the worst double and the
   last resource.


.. sourcecode:: python

   sender = ProxySpy(Sender())  # NOTE: It takes an instance (not class)

   assert_that(sender.say(), is_("hi"))
   assert_that(sender.say, called())

   sender.say('boo!')  # interface mismatch exception


.. sourcecode:: python

   Traceback (most recent call last):
   ...
   TypeError: Sender.say() takes exactly 1 argument (2 given)


.. index::
   single: Mock

Mock
====

Hint: *Mock forces the predefined script.*

Mock objects may be programmed with a sequence of method calls. Later, the double must
receive exactly the same sequence of invocations (including argument values). If the
sequence does not match, an AssertionError is raised. "free" mocks are provided too:


.. sourcecode:: python

   with Mock() as smtp:
       smtp.helo()
       smtp.mail(ANY_ARG)
       smtp.rcpt("bill@apple.com")
       smtp.data(ANY_ARG).returns(True).times(2)

   smtp.helo()
   smtp.mail("poormen@home.net")
   smtp.rcpt("bill@apple.com")
   smtp.data("somebody there?")
   smtp.data("I am afraid..")

   assert_that(smtp, verify())


``verify()`` asserts invocation order. If your test does not require strict invocation
order just use ``any_order_verify()`` matcher instead:


.. sourcecode:: python

   with Mock() as mock:
       mock.foo()
       mock.bar()

   mock.bar()
   mock.foo()

   assert_that(mock, any_order_verify())


Programmed invocation sequence also may specify stubbed return values:


.. sourcecode:: python

   with Mock() as mock:
       mock.foo().returns(10)

   assert_that(mock.foo(), is_(10))
   assert_that(mock, verify())


=========
Reference
=========


.. index::
   single:  assert_that()

assert_that()
=============

CAUTION: Be ware about hamcrest assert_that()
---------------------------------------------

Note the `hamcrest assert_that()
<https://github.com/hamcrest/PyHamcrest/blob/master/hamcrest/core/assert_that.py#L39>`_
function has two different behavior depending of its arguments:

* ``assert_that(actual, matcher, [reason])``
  In this form the ``matcher`` is applied to the ``actual`` object. If the
  matcher fails, it raises AssertionError showing the optional reason.

* ``assert_that(value, [reason])``
  If the boolean interpretation of ``value`` is False, it raises
  AssertionError showing the optional reason.

It implies that something like:

.. sourcecode:: python

   assert_that(foo, bar)


If ``bar`` is not a matcher, the assertion is satisfied for any non-false ``foo``,
independently of the value of ``bar``. A more obvious example:

.. sourcecode:: python

   assert_that(2 + 2, 5)  # that assertion IS satisfied!

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
behavior for non stubbed methods is to return ``None`` (although it can be changed).


.. sourcecode:: python

   >>> stub = Stub()
   >>> stub.method()

This behavior may be customized in each test using the Python context manager facility:

.. sourcecode:: python

   with Stub() as stub:
    	stub.method(<args>).returns(<value>)


`Hamcrest <https://code.google.com/p/hamcrest/wiki/TutorialPython>`_ matchers may be used
to define amazing stub conditions:


.. sourcecode:: python

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


``all_of``, ``has_length``, ``less_than`` and ``greater_than`` are standard hamcrest matchers.


Stubs returning input
---------------------


.. sourcecode:: python

   def test_returns_input(self):
       with Stub() as stub:
           stub.foo(1).returns_input()

       assert_that(stub.foo(1), is_(1))


Stubs raising exceptions
------------------------


.. sourcecode:: python

   def test_raises(self):
       with Stub() as stub:
           stub.foo(2).raises(SomeException)

       with self.assertRaises(SomeException):
           stub.foo(2)


Changing default stub behavior
------------------------------

.. versionadded:: 1.7 - (thanks to `Eduardo Ferro`__)

__ https://bitbucket.org/DavidVilla/python-doublex/pull-request/4/stub-configuration-for-raise-an-error-when


Any non-stubbed method returns ``None``. But this behavior can be changed by means of ``set_default_behavior()`` function. It can be applied to any double class: ``Stub``, ``Spy``, ``ProxySpy`` or ``Mock``.

.. sourcecode:: python

   set_default_behavior(Stub, method_returning(20))
   stub  = Stub()
   assert_that(stub.unknown(), is_(20))

Or to a specific instance:


.. sourcecode:: python

   stub = Stub()
   set_default_behavior(stub, method_returning(20))
   assert_that(stub.unknown(), is_(20))

Also, it is possible to raise some exception:


.. sourcecode:: python

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

called()
--------

``called()`` matches method invocation (argument values are not relevant):


.. sourcecode:: python

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

with_args(): asserting calling argument values
----------------------------------------------

Match explicit argument values:


.. sourcecode:: python

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

   spy = Spy()

   spy.foo("abcd")

   assert_that(spy.foo, called().with_args(has_length(4)))
   assert_that(spy.foo, called().with_args(has_length(greater_than(3))))
   assert_that(spy.foo, called().with_args(has_length(less_than(5))))
   assert_that(spy.foo, never(called().with_args(has_length(greater_than(5)))))


``has_length``, ``less_than`` and ``greater_than`` are standard hamcrest matchers.


.. index::
   single:  hamcrest; anything()

anything(): asserting wildcard values
-------------------------------------

The ``anything()`` hamcrest matcher may be used to match any single value. That is useful when
only some arguments are relevant:


.. sourcecode:: python

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

with_some_args(): asserting just relevant arguments
---------------------------------------------------

.. versionadded:: 1.7

When a method have several arguments and you need to assert an invocation giving a specific value just for some of them, you may use the anything() matcher for the rest of them. That works but the resulting code is a bit dirty:


.. sourcecode:: python

   class Foo:
       def four_args_method(self, a, b, c, d, e=None):
           return 4

   spy = Spy(Foo)
   spy.four_args_method(1, 2, 'bob', 4)

   # only the 'c' argument is important in the test
   assert_that(spy.four_args_method,
               called().with_args(anything(), anything(), 'bob', anything()))
   # assert only 'b' argument
   assert_that(spy.four_args_method,
               called().with_args(anything(), 2, ANY_ARG))


The ``with_some_arg()`` allows to specify just some arguments, assuming all other can take any value. The same example using ``with_some_arg()``:


.. sourcecode:: python

   class Foo:
       def four_args_method(self, a, b, c, d):
           return 4

   spy = Spy(Foo)
   spy.four_args_method(1, 2, 'bob', 4)

   # only the 'c' argument is important in the test
   assert_that(spy.four_args_method,
               called().with_some_args(c='bob'))
   # assert only 'b' argument
   assert_that(spy.four_args_method,
               called().with_some_args(b=2))


This method may be used with both keyword and non-keyword arguments.

.. warning::
   Formal argument name is mandatory, so this is only applicable to restricted spies
   (those that are instantiated giving a collaborator).


.. index::
   single:  never()

never()
-------

Convenient replacement for ``hamcrest.is_not()``:


.. sourcecode:: python

   spy = Spy()

   assert_that(spy.m5, hamcrest.is_not(called()))  # is_not() works too
   assert_that(spy.m5, never(called()))            # but prefer never() due to better error report messages


.. index::
   single:  times()

times(): asserting number of calls
----------------------------------


.. sourcecode:: python

   spy = Spy()

   spy.foo()
   spy.foo(1)
   spy.foo(1)
   spy.foo(2)

   assert_that(spy.never, never(called()))                      # = 0 times
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


``anything``, ``all_of``, ``less_than`` and ``greater_than`` are standard hamcrest matchers.


calls: low-level access to invocation records
---------------------------------------------

.. versionadded:: 1.6.3

Invocation over spy methods are available in the ``calls`` attribute. You may use that to
get invocation argument values and perform complex assertions (i.e: check invocations
arguments were specific instances). However, you should prefer ``called()`` matcher
assertions over this. An example:


.. sourcecode:: python

   class TheCollaborator(object):
       def method(self, *args, **kargs):
           pass

   with Spy(TheCollaborator) as spy:
       spy.method(ANY_ARG).returns(100)

   spy.method(1, 2, 3)
   spy.method(key=2, val=5)

   assert_that(spy.method.calls[0].args, is_((1, 2, 3)))
   assert_that(spy.method.calls[1].kargs, is_(dict(key=2, val=5)))
   assert_that(spy.method.calls[1].retval, is_(100))


.. index::
   single:  Properties

Properties
==========

**doublex** supports stub and spy properties in a pretty easy way in relation to other
frameworks like python-mock.

That requires two constraints:

* It does not support "free" doubles. ie: you must give a collaborator in the constructor.
* collaborator must be a new-style class. See the next example.


Stubbing properties
-------------------


.. sourcecode:: python

   with Spy(Collaborator) as spy:
       spy.prop = 2  # stubbing 'prop' value

   assert_that(spy.prop, is_(2))  # double property getter invoked


Spying properties
-----------------

Continuing previous example:


.. sourcecode:: python

   class Collaborator(object):
       @property
       def prop(self):
           return 1

       @prop.setter
       def prop(self, value):
           pass

   spy = Spy(Collaborator)
   value = spy.prop

   assert_that(spy, property_got('prop'))  # property 'prop' was read.

   spy.prop = 4
   spy.prop = 5
   spy.prop = 5

   assert_that(spy, property_set('prop'))  # was set to any value
   assert_that(spy, property_set('prop').to(4))
   assert_that(spy, property_set('prop').to(5).times(2))
   assert_that(spy, never(property_set('prop').to(6)))


Ad-hoc stub methods
===================

Create a standalone stub method directly over any instance (even no doubles):


.. sourcecode:: python

   collaborator = Collaborator()
   collaborator.foo = method_returning("bye")
   assert_that(collaborator.foo(), is_("bye"))

   collaborator.foo = method_raising(SomeException)
   collaborator.foo()  # raises SomeException



   Traceback (most recent call last):
   ...
   SomeException


.. index::
   single:  Stub observers

Stub observers
==============

Stub observers allow you to execute extra code (similar to python-mock "side effects", but easier):


.. sourcecode:: python

   class Observer(object):
       def __init__(self):
           self.state = None

       def update(self, *args, **kargs):
           self.state = args[0]

   observer = Observer()
   stub = Stub()
   stub.foo.attach(observer.update)
   stub.foo(2)

   assert_that(observer.state, is_(2))


.. index::
   single:  Stub delegates

Stub delegates
==============

The value returned by the stub may be delegated from a function, method or other
callable...


.. sourcecode:: python

   def get_user():
       return "Freddy"

   with Stub() as stub:
       stub.user().delegates(get_user)
       stub.foo().delegates(lambda: "hello")

   assert_that(stub.user(), is_("Freddy"))
   assert_that(stub.foo(), is_("hello"))


It may be delegated from iterables or generators too!:


.. sourcecode:: python

   with Stub() as stub:
       stub.foo().delegates([1, 2, 3])

   assert_that(stub.foo(), is_(1))
   assert_that(stub.foo(), is_(2))
   assert_that(stub.foo(), is_(3))


.. index::
   single:  Mimic doubles

Mimic doubles
=============

Usually double instances behave as collaborator surrogates, but they do not expose the
same class hierarchy, and usually this is pretty enough when the code uses "duck typing":

.. testsetup:: mimic

   class A(object):
       pass

   class B(A):
       pass



.. sourcecode:: python

   >>> spy = Spy(B())
   >>> isinstance(spy, Spy)
   True
   >>> isinstance(spy, B)
   False


But some third party library DOES strict type checking using ``isinstance()``. That invalidates our doubles. For these cases you can use Mimic's. Mimic class can decorate any double class to achieve full replacement instances (Liskov principle):


.. sourcecode:: python

   >>> spy = Mimic(Spy, B)
   >>> isinstance(spy, B)
   True
   >>> isinstance(spy, A)
   True
   >>> isinstance(spy, Spy)
   True
   >>> isinstance(spy, Stub)
   True
   >>> isinstance(spy, object)
   True



Asynchronous spy assertions
===========================

.. versionadded:: 1.5.1

Sometimes interaction among your SUT class and their collaborators does not meet a
synchronous behavior. That may happen when the SUT performs collaborator invocations in a
different thread, or when the invocation pass across a message queue, publish/subscribe
service, etc.

Something like that:


.. sourcecode:: python

   class Collaborator(object):
       def write(self, data):
           print "your code here"

   class SUT(object):
       def __init__(self, collaborator):
           self.collaborator = collaborator

       def some_method(self):
           thread.start_new_thread(self.collaborator.write, ("something",))


If you try to test your collaborator is called using a Spy, you will get a wrong behavior:


.. sourcecode:: python

   # THE WRONG WAY
   class AsyncTests(unittest.TestCase):
       def test_wrong_try_to_test_an_async_invocation(self):
           # given
           spy = Spy(Collaborator)
           sut = SUT(spy)

           # when
           sut.some_method()

           # then
           assert_that(spy.write, called())


due to the ``called()`` assertion may happen before the ``write()`` invocation, but not
always.

You may be tempted to put a sleep before the assertion, but this is a bad solution. A
right way to solve that issue is to use something like a barrier. The threading.Event
class may be used as a barrier. See this new test version:


.. sourcecode:: python

   # THE DIRTY WAY
   class AsyncTests(unittest.TestCase):
       def test_an_async_invocation_with_barrier(self):
           # given
           barrier = threading.Event()
           with Spy(Collaborator) as spy:
               spy.write.attach(lambda *args: barrier.set)

           sut = SUT(spy)

           # when
           sut.some_method()
           barrier.wait(1)

           # then
           assert_that(spy.write, called())


The ``spy.write.attach()`` is part of the doublex testing framework and provides
stub-observers. That is, a way to run arbitrary code when stubbed methods are called.

That works because the ``called()`` assertion is performed only when the spy release the
barrier. It the ``write()`` invocation never happen, the ``barrier.wait()`` continues
after 1 second and the test fail, as must do. When all is right, the barrier waits just
the required time.

Well, this mechanism is a doublex builtin in the last release (1.5.1) and provides the same
behavior in a clearer way. The next is functionally equivalent to the listing just above:


.. sourcecode:: python

   # THE DOUBLEX WAY
   class AsyncTests(unittest.TestCase):
       def test_test_an_async_invocation_with_doublex_async(self):
           # given
           spy = Spy(Collaborator)
           sut = SUT(spy)

           # when
           sut.some_method()

           # then
           assert_that(spy.write, called().async(timeout=1))


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
