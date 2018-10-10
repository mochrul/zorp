AM_CXXFLAGS=@ZORP_CXXFLAGS@
AM_LDFLAGS=@ZORP_LIBS@


sysconfdir = ${ZORP_SYSCONFDIR}
sbin_PROGRAMS = zorp

zorp_SOURCES = main.cc

sysconf_DATA = policy.py.http.sample policy.py.https.sample policy.py.ssh.sample

EXTRA_DIST = $(sysconf_DATA)
