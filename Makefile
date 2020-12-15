#!/usr/bin/make -f
# -*- mode:makefile -*-

URL_AUTH=svn+ssh://${ALIOTH_USER}@svn.debian.org/svn/python-modules/packages/doublex/trunk
URL_ANON=svn://svn.debian.org/svn/python-modules/packages/doublex/trunk
GITHUB=git@github.com:davidvilla/python-doublex.git

debian:
	if [ ! -z "$${ALIOTH_USER}" ]; then \
	    svn co ${URL_AUTH} -N; \
	else \
	    svn co ${URL_ANON} -N; \
	fi

	mv trunk/.svn .
	rmdir trunk
	svn up debian


.PHONY: docs doctests
docs:
	$(MAKE) -C docs

doctests:
	$(MAKE) -C doctests

push:
	git push
	git push ${GITHUB}
	git push --tags ${GITHUB}

pypi-release:
	$(RM) -f dist
	python3 setup.py sdist
	twine upload dist/*

clean:
	find . -name *.pyc -delete
	find . -name *.pyo -delete
	find . -name *~ -delete
	$(RM) -r *.egg-info MANIFEST
	$(RM) -r dist build *.egg-info .tox
	$(RM) -r slides/reveal.js
	$(MAKE) -C docs clean
	$(MAKE) -C doctests clean

vclean: clean
	$(RM) -r .svn debian
