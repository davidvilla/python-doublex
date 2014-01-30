.. index::
   single:  Stub delegates

.. _delegates:

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


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
