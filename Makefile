clean:
	find . -name *.pyc -delete
	find . -name *.pyo -delete
	find . -name *~ -delete
	$(RM) -r dist

vclean:
	$(RM) -r .svn debian

debian:
	svn co svn://svn.debian.org/svn/python-modules/packages/python-doublex/trunk -N
	mv trunk/.svn .
	svn up debian
