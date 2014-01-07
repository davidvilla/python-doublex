Release notes
=============

doublex 1.8
-----------

* NEW inline stubbing and mocking with :py:func:`when` and :py:func:`expect_call`. See
  `doc`__ and `tests`__.
* Added support for mocking properties. See `doc`__ and `tests`__.
* Testing with tox for Python 2.6, 2.7, 3.2 and 3.3.
* Documentation now at `<http://python-doublex.readthedocs.org>`_

__ http://python-doublex.readthedocs.org/en/latest/inline-setup.html
__ https://bitbucket.org/DavidVilla/python-doublex/src/7b22f6d23455712b3e8894e40ae6272fc852762e/doublex/test/unit_tests.py?at=default#cl-1482
__ http://python-doublex.readthedocs.org/en/latest/properties.html#mocking-properties
__ https://bitbucket.org/DavidVilla/python-doublex/src/7b22f6d23455712b3e8894e40ae6272fc852762e/doublex/test/unit_tests.py?at=default#cl-1204


doublex 1.7.2
-------------

* Added support for varargs methods (\*args, \*\*kargs). Fixes `issue 14`__.
* NEW tracer mechanism to log double invocations. See `test`__.
* NEW module level ``wait_that()`` function.

__ https://bitbucket.org/DavidVilla/python-doublex/issue/14/problem-spying-a-method-with-a-decorator
__ https://bitbucket.org/DavidVilla/python-doublex/src/df2b3bda0eef64b5ddc6d6b3cc5a6380fb98e132/doublex/test/unit_tests.py?at=default#cl-1414


doublex 1.7
-----------

* NEW ``with_some_args()`` matcher to specify just relevant argument values in spy assertions. See `doc`__ and `tests`__.
* NEW module level ``set_default_behavior()`` function to define behavior for non stubbed methods. Thanks to `Eduardo Ferro`__. See `doc`__ and `tests`__.

__ http://python-doublex.readthedocs.org/en/latest/reference.html#with-some-args-asserting-just-relevant-arguments
__ https://bitbucket.org/DavidVilla/python-doublex/src/147de5e7a52efae3c871c3065c082794b7272819/doublex/test/unit_tests.py?at=default#cl-1218
__ https://bitbucket.org/eferro
__ http://python-doublex.readthedocs.org/en/latest/reference.html#changing-default-stub-behavior
__ https://bitbucket.org/DavidVilla/python-doublex/src/147de5e7a52efae3c871c3065c082794b7272819/doublex/test/unit_tests.py?at=default#cl-1243


doublex 1.6.6
-------------

* bug fix update: Fixes `issue 11`__.

__ https://bitbucket.org/DavidVilla/python-doublex/issue/11/there-are-no-stub-empy_stub-in-the


doublex 1.6.5
-------------

* bug fix update: Fixes `issue 10`__.

__ https://bitbucket.org/DavidVilla/python-doublex/issue/10/any_order_verify-fails-when-method-are


doublex 1.6.4
-------------

* Asynchronous spy assertion race condition bug fixed.
* Reading double attributes returns collaborator.class attribute values by default.

doublex 1.6.2
-------------

* Invocation stubbed return value is now stored.

* New low level spy API: double "calls" property provides access to invocations and their
  argument values. Each 'call' has an "args" sequence and "kargs dictionary". This
  provides support to perform individual assertions and direct access to invocation
  argument values. (see `test`__ and `doc`__).

__ https://bitbucket.org/DavidVilla/python-doublex/src/ce8cdff71b8e3528380c305bf7d9ca75a64f6460/doublex/test/unit_tests.py?at=v1.6.2#cl-271
__ http://python-doublex.readthedocs.org/en/latest/reference.html#calls-low-level-access-to-invocation-records


doublex 1.6
-----------

* First release supporting Python 3 (up to Python 3.2) [fixes `issue 7`__].
* Ad-hoc stub attributes (see `test`__).
* Partial support for non native Python functions.
* ProxySpy propagated stubbed invocations too (see `test`__).

__ https://bitbucket.org/DavidVilla/python-doublex/issue/7
__ https://bitbucket.org/DavidVilla/python-doublex/src/cb8ba0df2e024d602fed236bb5ed5a7ceee91b20/doublex/test/unit_tests.py?at=v1.6#cl-146
__ https://bitbucket.org/DavidVilla/python-doublex/src/cb8ba0df2e024d602fed236bb5ed5a7ceee91b20/doublex/test/unit_tests.py?at=v1.6#cl-340


doublex 1.5.1
-------------

This release includes support for asynchronous spy assertions. See `this blog post
<http://crysol.org/es/node/1688>`_ for the time being, soon in the official documentation.


doublex/pyDoubles 1.5
---------------------

Since this release, doublex supports the pyDoubles API by means a wrapper. See `pyDoubles <http://python-doublex.readthedocs.org/en/latest/pyDoubles.html>`_ for details.

In most cases the only required change in your code is the ``import`` sentence, that change from::

    import pyDoubles.framework.*

to::

    from doublex.pyDoubles import *


If you have problems migrating to the 1.5 release or migrating from pyDoubles to
doublex, please ask for help in the `discussion forum
<https://groups.google.com/forum/?fromgroups#!forum/pydoubles>`_ or in the `issue tracker
<https://bitbucket.org/DavidVilla/python-doublex/issues>`_.


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End: