.. index::
   single:  Mimic doubles

Mimic doubles
=============

Usually double instances behave as collaborator surrogates, but they do not expose the
same class hierarchy, and usually this is pretty enough when the code uses "duck typing":

.. testsetup:: mimic
.. sourcecode:: python

   class A(object):
       pass

   class B(A):
       pass



.. sourcecode:: python

   >>> from doublex import Spy
   >>> spy = Spy(B())
   >>> isinstance(spy, Spy)
   True
   >>> isinstance(spy, B)
   False


But some third party library DOES strict type checking using ``isinstance()``. That
invalidates our doubles. For these cases you can use Mimic's. Mimic class decorates any
double class to achieve full replacement instances (Liskov principle):


.. sourcecode:: python

   >>> from doublex import Stub, Mimic
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


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
