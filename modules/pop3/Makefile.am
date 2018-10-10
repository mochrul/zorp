SUBDIRS = messages

pkgdatadir = @ZORP_PYTHON_DIR@
pkglibdir = ${ZORP_LIBDIR}
AM_LDFLAGS = @MODULES_LIBS@
AM_CXXFLAGS = @MODULES_CXXFLAGS@

pkglib_LTLIBRARIES = libpop3.la

libpop3_la_SOURCES = pop3.cc pop3misc.cc pop3cmd.cc pop3policy.cc pop3data.cc pop3auth.cc  pop3cmd.h pop3.h pop3policy.h pop3misc.h pop3data.h
