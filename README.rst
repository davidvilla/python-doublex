==============
python-doublex
==============

A powerful test doubles framework for Python.

This started as a try to improve and simplify pyDoubles codebase and API

Source repository is: https://bitbucket.org/DavidVilla/python-doublex


Design principles
=================

- Doubles have not public api specific methods. It avoid silent misspelling.
- non-proxified doubles does not require collaborator instances, they may use classes
- hamcrest.assert_that used for all assertions
- Mock invocation order is required by default
- Compatible with old and new style classes


Doubles
=======

"free" Stub
-----------

::

 # given
 stub = Stub()
 with stub:
     stub.foo('hi').returns(10)
     stub.hello(ANY_ARG).returns(False)
     stub.bye().raises(SomeException)

 # when
 result = stub.foo()

 # then
 assert_that(result, 10)


"verified" Stub
---------------

::

 class Collaborator:
     def hello(self):
         return "hello"

 with Stub(Collaborator) as stub
     stub.hello().raises(SomeException)
     stub.foo().returns(True)  # raises ApiMismatch exception
     stub.hello(1).returns(2)  # raises ApiMismatch exception


"free" Spy
----------

::

 # given
 with Spy() as sender:
     sender.helo().returns("OK")

 # when
 sender.send_mail('hi')
 sender.send_mail('foo@bar.net')

 # then
 assert_that(sender.helo(), "OK")
 assert_that(sender.send_mail, called())
 assert_that(sender.send_mail, called().times(2))
 assert_that(sender.send_mail, called_with('foo@bar.net'))


"verified" Spy
--------------

::

 class Sender:
     def say(self):
         return "hi"

     def send_mail(self, address, force=True):
         [some amazing code]

 sender = Spy(Sender)

 sender.bar()        # raises ApiMismatch exception
 sender.send_mail()  # raises ApiMismatch exception
 sender.send_mail(wrong=1)         # raises ApiMismatch exception
 sender.send_mail('foo', wrong=1)  # raises ApiMismatch exception


ProxySpy
--------

::

 sender = Spy(Sender())  # must give an instance

 sender.say('boo!')  # raises ApiMismatch exception

 assert_that(sender.say(), "hi")
 assert_that(sender.say, called())


"free" Mock
-----------

::

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

 assert_that(smtp, meets_expectations())


"verified" Mock
---------------

::

 class SMTP:
     def helo(self):
         [...]
     def mail(self, address):
         [...]
     def rcpt(self, address):
         [...]

 with Mock(STMP) as smtp:
     smtp.wrong()  # raises ApiMismatch exception
     smtp.mail()   # raises ApiMismatch exception


stub methods
------------

::

 collaborator = Collaborator()
 collaborator.foo = method_returning("bye")
 assertEquals("bye", self.collaborator.foo())

 collaborator.foo = method_raising(SomeException)
 collaborator.foo()  # raises SomeException


doublex matchers
================

called
------

called() matches any invocation to a method::

 spy.Spy()
 spy.m1()
 spy.m2(None)
 spy.m3("hi", 3.0)
 spy.m4([1, 2])

 assert_that(spy.m1, called())
 assert_that(spy.m2, called())
 assert_that(spy.m3, called())
 assert_that(spy.m4, called())


called_with
-----------

called_with() matches specific arguments::

 spy.Spy()
 spy.m1()
 spy.m2(None)
 spy.m3("hi", 3.0)
 spy.m4([1, 2])

 assert_that(spy.m1, called_with())
 assert_that(spy.m2, called_with(None))
 assert_that(spy.m3, called_with("hi", 3.0))
 assert_that(spy.m4, called_with([1, 2]))



matchers, matchers, hamcrest matchers...
========================================

doublex support all hamcrest matchers, and their amazing combinations.

checking spied calling args
---------------------------

::

 spy = Spy()
 spy.foo("abcd")

 assert_that(spy.foo, called_with(has_length(4)))
 assert_that(spy.foo, called_with(has_length(greater_than(3))))
 assert_that(spy.foo, called_with(has_length(less_than(5))))
 assert_that(spy.foo, is_not(called_with(has_length(greater_than(5)))))


stubbing
--------

::

 with Spy() as spy:
     spy.foo(has_length(less_than(4))).returns('<4')
     spy.foo(has_length(4)).returns('four')
     spy.foo(has_length(
		all_of(greater_than(4),
                       less_than(8)))).returns('4<x<8')
     spy.foo(has_length(greater_than(8))).returns('>8')

 assert_that(spy.foo((1, 2)), is_('<4'))
 assert_that(spy.foo('abcd'), is_('four'))
 assert_that(spy.foo('abcde'), is_('4<x<8'))
 assert_that(spy.foo([0] * 9), is_('>8'))


checking invocation 'times'
---------------------------

::

 spy.foo()
 spy.foo(1)
 spy.foo(1)
 spy.foo(2)

 assert_that(spy.never, is_not(called()))                     # = 0 times
 assert_that(spy.foo, called())                               # > 0
 assert_that(spy.foo, called().times(greater_than(0)))        # > 0 (same)
 assert_that(spy.foo, called().times(4))                      # = 4
 assert_that(spy.foo, called().times(greater_than(2)))        # > 2
 assert_that(spy.foo, called().times(less_than(6)))           # < 6

 assert_that(spy.foo, is_not(called_with(5)))                 # = 0 times
 assert_that(spy.foo, called_with().times(1))                 # = 1
 assert_that(spy.foo, called_with(anything()))                # > 0
 assert_that(spy.foo, called_with(anything()).times(4))       # = 4
 assert_that(spy.foo, called_with(1).times(2))                # = 2
 assert_that(spy.foo, called_with(1).times(greater_than(1)))  # > 1
 assert_that(spy.foo, called_with(1).times(less_than(5)))     # < 5


Stub observers
==============

Stub observers allow you to execute extra code (similar to python-mock "side effects")::

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


Stub delegates
==============

The value returned by the stub may be delegated to function, method or other callable...::

 with Stub() as stub:
     stub.foo().delegates(lambda: "hello")

 assert_that(stub.foo(), is_("hello"))

It may be delegated to iterators or generators too!::

 with Stub() as stub:
     stub.foo().delegates([1, 2, 3])

 assert_that(stub.foo(), is_(1))
 assert_that(stub.foo(), is_(2))
 assert_that(stub.foo(), is_(3))
