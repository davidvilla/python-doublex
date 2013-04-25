#!/usr/bin/make -f
# -*- mode:makefile -*-

clean:
	find . -name *.pyc -delete
	find . -name *.pyo -delete
	find . -name *~ -delete
	$(RM) -r dist build *.egg-info
	$(RM) -r .svn debian MANIFEST
	$(RM) -r *.egg-info
	$(RM) -r slides/reveal.js
