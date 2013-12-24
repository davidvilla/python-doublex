.. image:: https://pypip.in/v/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Number of PyPI downloads


Powerful test doubles framework for Python.

design principles
-----------------

* doubles should not have public API framework methods. It avoid silent misspelling.
* doubles do not require collaborator instances, just classes, and never instantiate them.
* ``assert_that()`` is used for ALL assertions.
* mock invocation order is required by default.
* compatible with old and new style classes.


a trivial example
-----------------

.. sourcecode:: python

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

* `documentation    <http://doublex.readthedocs.org/>`_
* `release notes    <http://doublex.readthedocs.org/en/latest/release-notes.html>`_
* `slides           <http://arco.esi.uclm.es/~david.villa/python-doublex/slides>`_
* `sources          <https://bitbucket.org/DavidVilla/python-doublex>`_
* `PyPI project     <http://pypi.python.org/pypi/doublex>`_
* `Crate page       <https://crate.io/packages/doublex/>`_
* `buildbot job     <https://fowler.esi.uclm.es:8010/builders/doublex>`_
* `other doubles    <http://garybernhardt.github.io/python-mock-comparison/>`_


Debian
------

* package: http://packages.debian.org/source/sid/doublex
* amateur debian package at: ``deb http://babel.esi.uclm.es/arco/ sid main``
* official ubuntu package: https://launchpad.net/ubuntu/+source/doublex
* debian dir: ``svn://svn.debian.org/svn/python-modules/packages/doublex/trunk``


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
