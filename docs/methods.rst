.. _ad-hoc methods:

Ad-hoc stub methods
===================

Create a standalone stub method directly over any instance (even no doubles), with :py:func:`method_returning` and :py:func:`method_raising`:


.. sourcecode:: python

   from doublex import method_returning, method_raising, assert_that

   collaborator = Collaborator()
   collaborator.foo = method_returning("bye")
   assert_that(collaborator.foo(), is_("bye"))

   collaborator.foo = method_raising(SomeException)
   collaborator.foo()  # raises SomeException



   Traceback (most recent call last):
   ...
   SomeException



.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
