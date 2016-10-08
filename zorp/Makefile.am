pkglibdir=$(libdir)/zorp
pkglibexecdir=$(libdir)/zorp
LIBS=@ZORP_LIBS@


pkglibexec_PROGRAMS = zorp

zorp_SOURCES = main.cc

sysconf_DATA = policy.py.http.sample policy.py.https.sample policy.py.ssh.sample

EXTRA_DIST = $(sysconf_DATA)
