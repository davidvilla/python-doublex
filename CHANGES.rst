20131227
========

- Release 1.7.4
- Double methods copy original __name__ attribute
- Mock support for properties

20131107
========

- Release 1.7.2
- [NEW] support for varargs (*args, **kargs) methods
- [NEW] tracer for doubles, methods and properties

20130712
========

- Release 1.6.8
- [NEW] with_some_args matcher
- [NEW] set_default_behavior module function to define behavior for non stubbed methods.

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
- async race condition bug fixed

20130211
========

- Access to spy invocations with _method_.calls

20130110
========

- Release 1.6
- Ad-hoc stub attributes
- AttributeFactory callable types: function, method (Closes: #bitbucket:issue/7)
- BuiltingSignature for non Python functions

20121118
========

- ProxySpy propagates stubbed invocations too

20121025
========

- Merge feature-async branch: Spy async checking

20121008
========

- release 1.5 to replace pyDoubles

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
