calls: low-level access to invocation records
---------------------------------------------

.. versionadded:: 1.6.3

Invocation over spy methods are available in the ``calls`` attribute. You may use that to
get invocation argument values and perform complex assertions (i.e: check invocations
arguments were specific instances). However, you should prefer ``called()`` matcher
assertions over this. An example:


.. sourcecode:: python

   from doublex import Spy, assert_that, ANY_ARG, is_

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


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
