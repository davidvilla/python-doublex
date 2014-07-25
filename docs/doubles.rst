=======
Doubles
=======

Some very basic examples are shown below. Remember that test doubles are created to be
invoked by your `SUT <http://en.wikipedia.org/wiki/System_under_test>`_, and a RealWorld™
test never directly invokes doubles.  Here we do it that way, but just for simplicity.

.. index::
   single: Stub

.. _stub:

Stub
====

Hint: *Stubs tell you what you wanna hear.*

A ``Stub`` is a double object that may be programmed to return specified values depending
on method invocations and their arguments. You must use a context (the ``with`` keyword)
for that.

Invocations over the ``Stub`` must meet the collaborator interface:

.. testsetup:: *

   import unittest

   class SomeException(Exception):
       pass

   class Collaborator(object):
       def hello(self):
           return "hello"

       def add(self, a, b):
           return a + b



.. sourcecode:: python

   from doublex import Stub, ANY_ARG, assert_that, is_

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

   from doublex import Stub, assert_that, is_

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

   from hamcrest import contains_string
   from doublex import Spy, assert_that, called

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

   from doublex import Stub, assert_that

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

   from doublex import ProxySpy, assert_that

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

.. _verify:

Mock
====

Hint: *Mock forces the predefined script.*

Mock objects may be programmed with a sequence of method calls. Later, the double must
receive exactly the same sequence of invocations (including argument values). If the
sequence does not match, an AssertionError is raised. "free" mocks are provided too:


.. sourcecode:: python

   from doublex import Mock, assert_that, verify

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

   from doublex import Mock, assert_that, any_order_verify

   with Mock() as mock:
       mock.foo()
       mock.bar()

   mock.bar()
   mock.foo()

   assert_that(mock, any_order_verify())


Programmed invocation sequence also may specify stubbed return values:


.. sourcecode:: python

   from doublex import Mock, assert_that

   with Mock() as mock:
       mock.foo().returns(10)

   assert_that(mock.foo(), is_(10))
   assert_that(mock, verify())


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
