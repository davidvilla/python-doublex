#!/usr/bin/make -f
# -*- mode:makefile -*-

URL_AUTH=svn+ssh://${ALIOTH_USER}@svn.debian.org/svn/python-modules/packages/doublex/trunk
URL_ANON=svn://svn.debian.org/svn/python-modules/packages/doublex/trunk

debian:
	if [ ! -z "$${ALIOTH_USER}" ]; then \
	    svn co ${URL_AUTH} -N; \
	else \
	    svn co ${URL_ANON} -N; \
	fi

	mv trunk/.svn .
	rmdir trunk
	svn up debian

wiki:
	hg clone ssh://hg@bitbucket.org/DavidVilla/python-doublex/wiki

clean:
	find . -name *.pyc -delete
	find . -name *.pyo -delete
	find . -name *~ -delete
	$(RM) -r dist build *.egg-info .tox
	$(RM) -r .svn debian MANIFEST
	$(RM) -r *.egg-info
	$(RM) -r slides/reveal.js
