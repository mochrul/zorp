SUBDIRS = . tests

pkgdatadir = @ZORP_PYTHON_DIR@
pkglibdir = ${ZORP_LIBDIR}

AM_LDFLAGS     = @MODULES_LIBS@
TEST_CXXFLAGS = @MODULES_CXXFLAGS@


AM_CXXFLAGS = $(TEST_CXXFLAGS)

pkglib_LTLIBRARIES = libtelnet.la

libtelnet_la_SOURCES = telnet.cc telnetpolicy.cc telnetsuboption.cc telnet.h telnetpolicy.h telnetsuboption.h telnettls.cc telnettls.h telnetprotocol.cc telnetprotocol.h telnetstate.cc telnetstate.h telnetlineedit.cc telnetlineedit.h telnetoption.cc telnetoption.h
