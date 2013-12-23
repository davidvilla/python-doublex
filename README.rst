.. image:: https://pypip.in/v/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/doublex/badge.png
    :target: https://crate.io/packages/doublex/
    :alt: Number of PyPI downloads

=======
doublex
=======

A powerful test doubles framework for Python.

**Design principles**

* doubles should not have public API framework methods. It avoid silent misspelling.
* doubles do not require collaborator instances, just classes, and never instantiate them.
* ``assert_that()`` is used for ALL assertions.
* mock invocation order is required by default.
* compatible with old and new style classes.


Important links
---------------

* `documentation        <https://bitbucket.org/DavidVilla/python-doublex/wiki>`_
* `release notes        <https://bitbucket.org/DavidVilla/python-doublex/wiki/Home#rst-header-release-notes>`_
* `slides               <http://arco.esi.uclm.es/~david.villa/python-doublex/slides>`_
* `sources              <https://bitbucket.org/DavidVilla/python-doublex>`_
* `PyPI project         <http://pypi.python.org/pypi/doublex>`_
* `Crate page           <https://crate.io/packages/doublex/>`_
* `buildbot job         <https://fowler.esi.uclm.es:8010/builders/doublex>`_
* `other Python doubles libraries <http://garybernhardt.github.io/python-mock-comparison/>`_


Debian
------

* package: http://packages.debian.org/source/sid/doublex
* amateur debian package at: ``deb http://babel.esi.uclm.es/arco/ sid main``
* official ubuntu package: https://launchpad.net/ubuntu/+source/doublex
* debian dir: ``svn://svn.debian.org/svn/python-modules/packages/doublex/trunk``
