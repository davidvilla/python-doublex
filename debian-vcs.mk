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

clean:
	$(RM) -r .svn debian MANIFEST
