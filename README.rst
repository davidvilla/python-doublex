python-doublex
==============

This is a try to improve and simplify pyDoubles[1] codebase and API

[1] https://bitbucket.org/carlosble/pydoubles


Design principles
-----------------

- Doubles have not public api specific methods. It avoid silent misspelling.
- non-proxified doubles does not require collaborator instances, they may use classes
- hamcrest.assert_that used for all assertions
- Mock invocation order is required by default
- Compatible with old and new style classes


"empty Stub"
------------

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
     def foo(self):
         return "foo"

 with Stub(Collaborator) as stub
     stub.foo().raises(SomeException)
     stub.bar().returns(True)  # raises ApiMismatch exception
     stub.foo(1).returns(2)    # raises ApiMismatch exception


"empty" Spy
-----------

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


"empty" Mock
------------

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


hamcrest matchers
-----------------

doublex support all hamcrest matchers, and amazing combinations, for happened
invocations::

 spy = Spy()
 spy.foo("abcd")

 assert_that(spy.foo, called_with(has_length(4)))
 assert_that(spy.foo, called_with(has_length(greater_than(3))))
 assert_that(spy.foo, called_with(has_length(less_than(5))))
 assert_that(spy.foo, is_not(called_with(has_length(greater_than(5)))))

and for stubbed calls:

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
