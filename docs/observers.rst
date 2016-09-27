.. index::
   single:  Stub observers

.. _observers:

Stub observers
==============

Stub observers allow you to execute extra code (similar to python-mock "side effects", but
easier):


.. sourcecode:: python

   class Observer(object):
       def __init__(self):
           self.state = None

       def notify(self, *args, **kargs):
           self.state = args[0]

   observer = Observer()
   stub = Stub()
   stub.foo.attach(observer.notify)
   stub.foo(2)

   assert_that(observer.state, is_(2))


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
