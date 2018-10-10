SUBDIRS = . tests

pkgdatadir = @ZORP_PYTHON_DIR@
pkglibdir = ${ZORP_LIBDIR}
AM_LDFLAGS = @MODULES_LIBS@
AM_CXXFLAGS = @MODULES_CXXFLAGS@

pkglib_LTLIBRARIES = libsmtp.la

libsmtp_la_SOURCES = smtp.cc smtpcmd.cc smtpdata.cc smtpmsg.cc smtppolicy.cc smtp.h smtpmsg.h
