.. image:: https://pypip.in/v/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/davidvilla/python-doublex.svg?branch=master
    :target: https://travis-ci.org/davidvilla/python-doublex
    :alt: Travis CI status

.. image:: https://pypip.in/py_versions/doublex/badge.png
    :target: https://pypi.pthon.org/pypi/doublex/
    :alt: Supported Python Versions

.. image:: https://pypip.in/license/doublex/badge.png
    :target: https://pypi.pthon.org/pypi/doublex/
    :alt: License

Powerful test doubles framework for Python


[
`install   <http://python-doublex.readthedocs.org/en/latest/install.html>`_ |
`docs      <http://python-doublex.readthedocs.org/>`_ |
`changelog <http://python-doublex.readthedocs.org/en/latest/release-notes.html>`_ |
`sources   <https://bitbucket.org/DavidVilla/python-doublex>`_ |
`issues    <https://bitbucket.org/DavidVilla/python-doublex/issues>`_ |
`PyPI      <http://pypi.python.org/pypi/doublex>`_ |
`buildbot  <http://fowler.esi.uclm.es:8010/builders/doublex>`_
]


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

See more about `doublex doubles <http://python-doublex.readthedocs.org/en/latest/reference.html#doubles>`_.


Features
--------

* doubles have not public API framework methods. It could cause silent misspelling.
* doubles do not require collaborator instances, just classes, and it never instantiate them.
* ``assert_that()`` is used for ALL assertions.
* mock invocation order is relevant by default.
* supports old and new style classes.
* **supports Python versions: 2.6, 2.7, 3.2, 3.3, 3.4**


Debian
^^^^^^

* `official package <http://packages.debian.org/source/sid/doublex>`_ (may be outdated)
* amateur repository: ``deb http://babel.esi.uclm.es/arco/ sid main`` (always updated)
* `official ubuntu package  <https://launchpad.net/ubuntu/+source/doublex>`_
* debian dir: ``svn://svn.debian.org/svn/python-modules/packages/doublex/trunk``


related
-------

* `slides           <http://arco.esi.uclm.es/~david.villa/python-doublex/slides>`_
* `pyDoubles        <http://python-doublex.readthedocs.org/en/latest/pyDoubles.html>`_
* `crate            <https://crate.io/packages/doublex/>`_
* `github clone     <https://github.com/davidvilla/python-doublex>`_
* `other doubles    <http://garybernhardt.github.io/python-mock-comparison/>`_
* `ludibrio        <https://pypi.python.org/pypi/ludibrio>`_


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End: