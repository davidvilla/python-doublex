20141126
========

- Release 1.8.2
- Bug fixed: https://bitbucket.org/DavidVilla/python-doublex/issue/22
- returns_input() may return several parameters, fixes
- delegates() accepts dictionaries.
- method_returning() and assert_raises() are now spies:
  https://bitbucket.org/DavidVilla/python-doublex/issue/21


20140107
========
- Release 1.8.1
- PyHamcrest must be a requirement. Thanks to Javier Santacruz and Guillermo Pascual
  https://bitbucket.org/DavidVilla/python-doublex/pull-request/7
  https://bitbucket.org/DavidVilla/python-doublex/issue/18

20140101
========

- Release 1.8a
- [NEW] inline stubbing and mocking functions: when, expect_call (merge with feature-inline-stubbing)
- [NEW] Testing Python 2.6, 2.7, 3.2 and 3.3 using tox
- [NEW] Add AttributeFactory type: wrapper_descriptor for builtin method (such as list.__setitem__)

20131227
========

- [NEW] Double methods copy original __name__ attribute
- [NEW] Mock support for properties

20131107
========

- Release 1.7.2
- [NEW] support for varargs (*args, **kargs) methods
- [NEW] tracer for doubles, methods and properties

20130712
========

- Release 1.6.8
- [NEW] with_some_args matcher
- [NEW] set_default_behavior() module function to define behavior for non stubbed methods.

20130513
========

- ANY_ARG is not allowed as keyword value
- ANY_ARG must be the last positional argument value

20130427
========

- Release 1.6.6
- [FIXED] stub/empty_stub were missing in pyDoubles wrapper

20130215
========

- Release 1.6.3
- [FIXED] async race condition bug

20130211
========

- [NEW] Access to spy invocations with _method_.calls

20130110
========

- Release 1.6
- [NEW] Ad-hoc stub attributes
- [NEW] AttributeFactory callable types: function, method (Closes: #bitbucket:issue/7)
- [NEW] BuiltingSignature for non Python functions

20121118
========

- [NEW] ProxySpy propagates stubbed invocations too

20121025
========

- Merge feature-async branch: Spy async checking

20121008
========

- Release 1.5 to replace pyDoubles

20120928
========

- ANY_ARG must be different to any other thing.

20120911
========

- API CHANGE: called_with() is now called().with_args() (magmax suggestion)


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
.. End:
