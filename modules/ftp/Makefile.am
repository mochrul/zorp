SUBDIRS = tests

pkgdatadir = @ZORP_PYTHON_DIR@
pkglibdir = ${ZORP_LIBDIR}
AM_LDFLAGS = @MODULES_LIBS@
AM_CXXFLAGS = @MODULES_CXXFLAGS@

pkglib_LTLIBRARIES = libftp.la

libftp_la_SOURCES = ftp.cc ftphash.cc ftpmsg.cc ftpcmd.cc ftpolicy.cc ftpdata.cc ftp.h ftpcmd.h ftphash.h ftpolicy.h ftpmsg.h
