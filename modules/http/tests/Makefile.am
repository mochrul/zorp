AM_LDFLAGS=@MODULETESTS_LIBS@ ../libhttp.la -lboost_unit_test_framework
AM_CXXFLAGS = @MODULES_CXXFLAGS@ -DBOOST_TEST_DYN_LINK=1

check_PROGRAMS = http_parse_url http_canon_url http_remove_cookie

http_parse_url_SOURCES = http_parse_url.cc

http_canon_url_SOURCES = http_canon_url.cc

http_remove_cookie_SOURCES = http_remove_cookie.cc

TESTS = http_parse_url http_canon_url http_remove_cookie
