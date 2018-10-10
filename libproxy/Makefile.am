SUBDIRS = zorp

AM_CXXFLAGS = @LIBZORP_CXXFLAGS@
lib_LTLIBRARIES = libzorpproxy.la

libzorpproxy_la_PRO_SOURCES =

libzorpproxy_la_LDFLAGS =	\
	@LIBZORP_LIBS@ \
	-version-info $(LIBZORP_LT_COMPAT_PL) \
	-export-dynamic

libzorpproxy_la_SOURCES = 		\
	dottransfer.cc			\
	errorloader.cc			\
	transfer2.cc                     \
        $(libzorpproxy_la_PRO_SOURCES)
