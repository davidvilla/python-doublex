=========
pyDoubles
=========

**IMPORTANT: pyDoubles support is removed since version 1.9.**


``doublex`` started as a attempt to improve and simplify the codebase and API of the
`pyDoubles <https://bitbucket.org/carlosble/pydoubles>`_ framework (by Carlos Ble).

Respect to pyDoubles, ``doublex`` has these features:

* Just hamcrest matchers (for all features).
* Only ProxySpy requires an instance. Other doubles accept a class too, but they never
  instantiate it.
* Properties may be stubbed and spied.
* Stub observers: Notify arbitrary hooks when methods are invoked. Useful to add "side
  effects".
* Stub delegates: Use callables, iterables or generators to create stub return values.
* Mimic doubles: doubles that inherit the same collaborator subclasses. This provides full
  `LSP <http://wikipedia.org/wiki/Liskov_substitution_principle>`_ for code that make
  strict type checking.

``doublex`` solves all the issues and supports all the feature requests notified in the
pyDoubles issue tracker:

* `assert keyword argument values <https://bitbucket.org/carlosble/pydoubles/issue/4/check-kwargs-keys-on-expect_calls>`_
* `assert that a method is called exactly one <https://bitbucket.org/carlosble/pydoubles/issue/2/check-if-method-was-called-only-once>`_
* `mocks impose invocation order <https://bitbucket.org/carlosble/pydoubles/issue/3/strictordermock>`_
* `doubles have framework public API <https://bitbucket.org/carlosble/pydoubles/issue/5/protection-agains-incorrect-usage>`_
* `stubs support keyword positional arguments <https://bitbucket.org/carlosble/pydoubles/issue/6/keyworded-positional-arguments-on-stubs>`_

And some other features requested in the user group:

* `doubles for properties <https://groups.google.com/d/topic/pydoubles/Mbca-oPhz90/discussion>`_
* `creating doubles without instantiating real class <https://groups.google.com/d/topic/pydoubles/rQSLluR-MgA/discussion>`_
* `using hamcrest with kwargs <https://groups.google.com/d/topic/pydoubles/J3CmxkE6D6E/discussion>`_


``doublex`` provides the pyDoubles API as a wrapper for easy transition to doublex for
pyDoubles users. However, there are small differences. The bigger diference is that
pyDoubles matchers are not supported anymore, although you may get the same feature using
standard hamcrest matchers. Anyway, formally provided pyDoubles matchers are available as
hamcrest aliases.

``doublex`` supports all the pyDoubles features and some more that can not be easily
backported. If you are a pyDoubles user you can run your tests using doublex.pyDoubles
module. However, we recommed the `native doublex API
<http://python-doublex.readthedocs.org/en/latest/reference.html#reference/>`_ for your new developments.

In most cases the only required change in your code is the ``import`` sentence, that change from:

.. sourcecode:: python

   import pyDoubles.framework.*

to:

.. sourcecode:: python

   from doublex.pyDoubles import *


See the old pyDoubles documentation at `<http://pydoubles.readthedocs.org>`__ (that was
formerly available in the pydoubles.org site).



.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
