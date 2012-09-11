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
 assert_that(result, is_(10))


"verified" Stub
---------------

::

 class Collaborator:
     def hello(self):
         return "hello"

 with Stub(Collaborator) as stub
     stub.hello().raises(SomeException)
     stub.foo().returns(True)  # interface mismatch exception
     stub.hello(1).returns(2)  # interface mismatch exception


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
 assert_that(sender.helo(), is_("OK"))
 assert_that(sender.send_mail, called())
 assert_that(sender.send_mail, called().times(2))
 assert_that(sender.send_mail, called().with_args('foo@bar.net'))


"verified" Spy
--------------

::

 class Sender:
     def say(self):
         return "hi"

     def send_mail(self, address, force=True):
         [some amazing code]

 sender = Spy(Sender)

 sender.bar()        # interface mismatch exception
 sender.send_mail()  # interface mismatch exception
 sender.send_mail(wrong=1)         # interface mismatch exception
 sender.send_mail('foo', wrong=1)  # interface mismatch exception


ProxySpy
--------

::

 sender = ProxySpy(Sender())  # NOTE this always takes an instance

 sender.say('boo!')  # interface mismatch exception

 assert_that(sender.say(), is_("hi"))
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

 assert_that(smtp, verify())

verify() assert invocation order. If your test does not require strict invocation order
just use any_order_verify() matcher instead::

 with Mock() as mock:
     mock.foo()
     mock.bar()

 mock.bar()
 mock.foo()

 assert_that(mock, any_order_verify())



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
     smtp.wrong()  # interface mismatch exception
     smtp.mail()   # interface mismatch exception


stub methods
------------

::

 collaborator = Collaborator()
 collaborator.foo = method_returning("bye")
 assertEquals("bye", self.collaborator.foo())

 collaborator.foo = method_raising(SomeException)
 collaborator.foo()  # raises SomeException


properties
----------

Doublex support stub and spy properties in a pretty easy way compared with other
frameworks like python-mock::

 class Collaborator(object):
     @property
     def prop(self):
         return 1

     @prop.setter
     def prop(self, value):
         pass

 with Spy(Collaborator) as spy:
     spy.prop = 2  # stubbing its value

 assert_that(spy.prop, is_(2))  # property getter invoked
 assert_that(spy, property_got('prop'))

 spy.prop = 4  # property setter invoked
 spy.prop = 5  # --
 spy.prop = 5  # --

 assert_that(spy, property_set('prop'))  # set to any value
 assert_that(spy, property_set('prop').to(4))
 assert_that(spy, property_set('prop').to(5).times(2))
 assert_that(spy, never(property_set('prop').to(8)))


To make property doubles is required to:

* You must Use "verified" doubles, ie: specify a collaborator in constructor.
* collaborator musy be new-style classes.


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


never
-----

::

 assert_that(spy.m5, is_not(called()))  # is_not() is a hamcrest matcher
 assert_that(spy.m5, never(called()))   # recommended (better report message)


with_args
---------

with_args() matches explicit argument values and hamcrest matchers::

 spy.Spy()

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

 assert_that(spy.m3, called().with_args(less_than(3)))
 assert_that(spy.m3, called().with_args(greater_than(1)))
 assert_that(spy.m6, called().with_args(name=contains_string("doe")))


ANY_ARG
=======

ANY_ARG is a special value that matches any value and any amount of values, including
no args. For example::

 spy.arg0()
 spy.arg1(1)
 spy.arg3(1, 2, 3)
 spy.arg_karg(1, key1='a')

 assert_that(spy.arg0, called().with_args(ANY_ARG))
 assert_that(spy.arg1, called().with_args(ANY_ARG))
 assert_that(spy.arg3, called().with_args(1, ANY_ARG))
 assert_that(spy.arg_karg, called().with_args(1, ANY_ARG))

Also for stubs::

 with Stub() as stub:
     stub.foo(ANY_ARG).returns(True)
     stub.bar(1, ANY_ARG).returns(True)

 assert_that(stub.foo(), is_(True))
 assert_that(stub.foo(1), is_(True))
 assert_that(stub.foo(key1='a'), is_(True))
 assert_that(stub.foo(1, 2, 3, key1='a', key2='b'), is_(True))

 assert_that(stub.foo(1, 2, 3), is_(True))
 assert_that(stub.foo(1, key1='a'), is_(True))

But, if you want match any single value, use hamcrest matcher anything()::

 spy.foo(1, 2, 3)
 assert_that(spy.foo, called().with_args(1, anything(), 3))

 spy.bar(1, key=2)
 assert_that(spy.bar, called().with_args(1, key=anything()))


matchers, matchers, hamcrest matchers...
========================================

doublex support all hamcrest matchers, and their amazing combinations.

checking spied calling args
---------------------------

::

 spy = Spy()
 spy.foo("abcd")

 assert_that(spy.foo, called().with_args(has_length(4)))
 assert_that(spy.foo, called().with_args(has_length(greater_than(3))))
 assert_that(spy.foo, called().with_args(has_length(less_than(5))))
 assert_that(spy.foo, never(called().with_args(has_length(greater_than(5)))))


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

 assert_that(spy.never, never(called()))                      # = 0 times
 assert_that(spy.foo, called())                               # > 0
 assert_that(spy.foo, called().times(greater_than(0)))        # > 0 (same)
 assert_that(spy.foo, called().times(4))                      # = 4
 assert_that(spy.foo, called().times(greater_than(2)))        # > 2
 assert_that(spy.foo, called().times(less_than(6)))           # < 6

 assert_that(spy.foo, never(called().with_args(5)))                  # = 0 times
 assert_that(spy.foo, called().with_args().times(1))                 # = 1
 assert_that(spy.foo, called().with_args(anything()))                # > 0
 assert_that(spy.foo, called().with_args(anything()).times(4))       # = 4
 assert_that(spy.foo, called().with_args(1).times(2))                # = 2
 assert_that(spy.foo, called().with_args(1).times(greater_than(1)))  # > 1
 assert_that(spy.foo, called().with_args(1).times(less_than(5)))     # < 5
 assert_that(spy.foo, called().with_args(1).times(
             all_of(greater_than(1), less_than(8))))                 # 1 < times < 8


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

 def get_user():
     return "Freddy"

 with Stub() as stub:
     stub.user().delegates(get_user)
     stub.foo().delegates(lambda: "hello")

 assert_that(stub.user(), is_("Freddy"))
 assert_that(stub.foo(), is_("hello"))

It may be delegated to iterables or generators too!::

 with Stub() as stub:
     stub.foo().delegates([1, 2, 3])

 assert_that(stub.foo(), is_(1))
 assert_that(stub.foo(), is_(2))
 assert_that(stub.foo(), is_(3))


Mimic doubles
=============

Usually double instances behave as collaborator subrogates, but they do not expose the
same class hierarchy, and usually this is pretty enough when the code uses "duck typing"::

 class A(object):
     pass

 class B(A):
     pass

 >>> spy = Spy(B())
 >>> isinstance(spy, Spy)
 True
 >>> isinstance(spy, B)
 False


But some third party library DOES strict type checking using isinstance() invalidating our
doubles. For these cases you can use Mimic's. Mimic class can decorate any double class to
achive full replacement (Liskov principle)::

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
