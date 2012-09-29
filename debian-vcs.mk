#!/usr/bin/make -f
# -*- mode:makefile -*-

URL=svn+ssh://${ALIOTH_USER}@svn.debian.org/svn/python-modules/packages/doublex/trunk

debian:
	svn co $(URL) -N
	mv trunk/.svn .
	rmdir trunk
	svn up debian

clean:
	find . -name *.pyc -delete
	find . -name *.pyo -delete
	find . -name *~ -delete
	$(RM) -r dist build
	$(RM) -r .svn debian MANIFEST
