.. image:: https://pypip.in/v/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Number of PyPI downloads


Powerful test doubles framework for Python.

design principles
-----------------

* doubles should not have public API framework methods. It avoids silent misspelling.
* doubles do not require collaborator instances, just classes, and it never instantiate them.
* ``assert_that()`` is used for ALL assertions.
* invocation order for mocks is relevant by default.
* supports old and new style classes.


a trivial example
-----------------

.. sourcecode:: python

   import unittest
   from doublex import Spy, assert_that, called

   class SpyUseExample(unittest.TestCase):
       def test_spy_example(self):
           # given
           spy = Spy(SomeCollaboratorClass)
           cut = YourClassUnderTest(spy)

           # when
           cut.a_method_that_call_the_collaborator()

           # then
           assert_that(spy.some_method, called())

See more about `doublex doubles <http://doublex.readthedocs.org/en/latest/reference.html#doubles>`_.


relevant links
--------------

* `install          <http://doublex.readthedocs.org/en/latest/install.html/>`_
* `documentation    <http://doublex.readthedocs.org/>`_
* `release notes    <http://doublex.readthedocs.org/en/latest/release-notes.html>`_
* `slides           <http://arco.esi.uclm.es/~david.villa/python-doublex/slides>`_
* `sources          <https://bitbucket.org/DavidVilla/python-doublex>`_
* `PyPI project     <http://pypi.python.org/pypi/doublex>`_
* `pyDoubles        <http://doublex.readthedocs.org/en/latest/pyDoubles.html>`_
* `crate            <https://crate.io/packages/doublex/>`_
* `buildbot job     <https://fowler.esi.uclm.es:8010/builders/doublex>`_
* `other doubles    <http://garybernhardt.github.io/python-mock-comparison/>`_


Debian
^^^^^^

* `official package <http://packages.debian.org/source/sid/doublex`_ (may be outdated)
* amateur repository: ``deb http://babel.esi.uclm.es/arco/ sid main`` (always updated)
* `official ubuntu package  <https://launchpad.net/ubuntu/+source/doublex>`_
* debian dir: ``svn://svn.debian.org/svn/python-modules/packages/doublex/trunk``


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
