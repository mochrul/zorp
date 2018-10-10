man_MANS = instances.conf.5 policy.py.5 zorp.8 zorpctl.8 zorpctl.conf.5

EXTRA_DIST = \
	instances.conf.5.xml \
	manpage_authors.xml \
	manpage_copyright.xml \
	policy.py.5.xml \
	zorp.8.xml \
	zorpctl.8.xml \
	zorpctl.conf.5.xml \
	zorp-entities.ent.in

SUFFIXES = .xml

%:: %.xml
	xsltproc --xinclude --nonet --catalogs --output $@ 'http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl' $<
