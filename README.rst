.. image:: https://img.shields.io/pypi/v/doublex.png
    :target: http://pypi.python.org/pypi/doublex
    :alt: Latest PyPI version


.. image:: https://img.shields.io/pypi/l/doublex.png?maxAge=2592000
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/doublex.png?maxAge=2592000
    :target: http://pypi.python.org/pypi/doublex
    :alt: Supported Python Versions

.. image:: https://github.com/DavidVilla/python-doublex/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/DavidVilla/python-doublex
    :alt: GitHub Actions CI status

Powerful test doubles framework for Python


[
`install   <http://python-doublex.readthedocs.org/en/latest/install.html>`_ |
`docs      <http://python-doublex.readthedocs.org/>`_ |
`changelog <http://python-doublex.readthedocs.org/en/latest/release-notes.html>`_ |
`sources   <https://bitbucket.org/DavidVilla/python-doublex>`_ |
`issues    <https://bitbucket.org/DavidVilla/python-doublex/issues>`_ |
`PyPI      <http://pypi.python.org/pypi/doublex>`_ |
`github clone <https://github.com/davidvilla/python-doublex>`_ 
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
* **supports Python versions: 3.6, 3.7, 3.8, 3.9, 3.10**


Debian
^^^^^^

* amateur repository: ``deb https://uclm-arco.github.io/debian sid main`` (always updated)
* `official package <http://packages.debian.org/source/sid/doublex>`_ (may be outdated)
* `official ubuntu package  <https://launchpad.net/ubuntu/+source/doublex>`_
* debian dir: ``svn://svn.debian.org/svn/python-modules/packages/doublex/trunk``


related
-------

* `slides           <http://arco.esi.uclm.es/~david.villa/python-doublex/slides>`_
* `pyDoubles        <http://python-doublex.readthedocs.org/en/latest/pyDoubles.html>`_
* `doublex-expects  <https://pypi.python.org/pypi/doublex-expects>`_
* `crate            <https://crate.io/packages/doublex/>`_
* `other doubles    <http://garybernhardt.github.io/python-mock-comparison/>`_
* `ludibrio         <https://pypi.python.org/pypi/ludibrio>`_
* `doubles          <https://github.com/uber/doubles>`_


.. Local Variables:
..  coding: utf-8
..  mode: rst
..  mode: flyspell
..  ispell-local-dictionary: "american"
..  fill-columnd: 90
.. End:
