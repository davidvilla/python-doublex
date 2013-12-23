Release notes
=============

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

__ https://bitbucket.org/DavidVilla/python-doublex/wiki/Home#rst-header-with-some-args-asserting-just-relevant-argument-values
__ https://bitbucket.org/DavidVilla/python-doublex/src/147de5e7a52efae3c871c3065c082794b7272819/doublex/test/unit_tests.py?at=default#cl-1218
__ https://bitbucket.org/eferro
__ https://bitbucket.org/DavidVilla/python-doublex/wiki/Home#rst-header-changing-default-stub-behavior
__ https://bitbucket.org/DavidVilla/python-doublex/src/147de5e7a52efae3c871c3065c082794b7272819/doublex/test/unit_tests.py?at=default#cl-1243


doublex 1.6.6
-------------

* bug fix update: Fixes `issue 11 <https://bitbucket.org/DavidVilla/python-doublex/issue/11/there-are-no-stub-empy_stub-in-the>`_.


doublex 1.6.5
-------------

* bug fix update: Fixes `issue 10 <https://bitbucket.org/DavidVilla/python-doublex/issue/10/any_order_verify-fails-when-method-are>`_.


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
  argument values. (see `test <https://bitbucket.org/DavidVilla/python-doublex/src/ce8cdff71b8e3528380c305bf7d9ca75a64f6460/doublex/test/unit_tests.py?at=v1.6.2#cl-271>`_ and `doc <https://bitbucket.org/DavidVilla/python-doublex/wiki/reference#!calls-low-level-access-to-invocation-records>`_).


doublex 1.6
-----------

* First release supporting Python-3 (up to Python-3.2) [fixes `issue 7 <https://bitbucket.org/DavidVilla/python-doublex/issue/7>`_.
* Ad-hoc stub attributes (see `test <https://bitbucket.org/DavidVilla/python-doublex/src/cb8ba0df2e024d602fed236bb5ed5a7ceee91b20/doublex/test/unit_tests.py?at=v1.6#cl-146>`_).
* Partial support for non native Python functions.
* ProxySpy propagated stubbed invocations too (see `test <https://bitbucket.org/DavidVilla/python-doublex/src/cb8ba0df2e024d602fed236bb5ed5a7ceee91b20/doublex/test/unit_tests.py?at=v1.6#cl-340>`_).

doublex 1.5.1
-------------

This release includes support for asynchronous spy assertions. See `this blog post
<http://crysol.org/es/node/1688>`_ for the time being, soon in the official documentation.


doublex/pyDoubles 1.5
---------------------

Since this release the pyDoubles API is provided as a wrapper to `doublex
<https://bitbucket.org/DavidVilla/python-doublex>`_. However, there are small
differences. pyDoubles matchers are not supported anymore, although you may get the same
feature using standard hamcrest matchers. Anyway, legacy pyDoubles matchers are provided
as hamcrest aliases.

In most cases the only required change in your code is the module name, that change from::

    import pyDoubles.framework.*

to::

    from doublex.pyDoubles import *


If you have problems migrating to the new 1.5 release or migrating from pyDoubles to
doublex, please ask for help in the `discussion forum
<https://groups.google.com/forum/?fromgroups#!forum/pydoubles>`_ or in the `issue tracker
<https://bitbucket.org/DavidVilla/python-doublex/issues>`_.
