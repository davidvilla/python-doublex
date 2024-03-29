.. _async_mode:

Asynchronous spies
==================

.. versionadded:: 1.5.1

Sometimes interaction among your SUT class and their collaborators does not meet a
synchronous behavior. That may happen when the SUT performs collaborator invocations in a
different thread, or when the invocation pass across a message queue, publish/subscribe
service, etc.

Something like that:


.. sourcecode:: python

   class Collaborator(object):
       def write(self, data):
           print("your code here")

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


due to the ``called()`` assertion may happen before the ``write()`` invocation, although
not always...

You may be tempted to put a sleep before the assertion, but this is a bad solution. A
right way to solve that issue is to use something like a barrier. The `threading.Event`__
may be used as a barrier. See this new test version:

__ http://docs.python.org/2/library/threading.html#event-objects


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


The ``spy.write.attach()`` is part of the doublex stub-observer `mechanism`__, a
way to run arbitrary code when stubbed methods are called.

__ http://python-doublex.readthedocs.org/en/latest/reference.html#stub-observers

That works because the ``called()`` assertion is performed only when the spy releases the
barrier. If the ``write()`` invocation never happens, the ``barrier.wait()`` continues
after 1 second but the test fails, as must do. When all is right, the barrier waits just
the required time.

Well, this mechanism is a doublex builtin (the ``async_mode`` matcher) since release 1.5.1
providing the same behavior in a clearer way. The next is functionally equivalent to the
listing just above:


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
           assert_that(spy.write, called().async_mode(timeout=1))


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-column: 90
.. End:
