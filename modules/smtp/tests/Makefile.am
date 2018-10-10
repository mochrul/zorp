AM_CXXFLAGS = @MODULES_CXXFLAGS@ -DBOOST_TEST_DYN_LINK=1
AM_LDFLAGS = @MODULETESTS_LIBS@ ../libsmtp.la -lboost_unit_test_framework

AM_DEFAULT_SOURCE_EXT = .cc

check_PROGRAMS = smtp_sanitize_addr smtp_parse smtp_request
TESTS = smtp_sanitize_addr smtp_parse smtp_request
