check_SCRIPTS = \
             test_deadlockcheck_algorithm.py  \
             test_detailedstatus_algorithm.py \
             test_getalgorithms.py            \
             test_getprocinfo_algorithm.py    \
             test_instances_conf.py           \
             test_loglevel_algorithm.py       \
             test_reload_algorithm.py         \
             test_start_algorithm.py          \
             test_status_algorithm.py         \
             test_szig.py                     \
             test_szig_walk_algorithm.py

AM_TESTS_ENVIRONMENT = PYTHONPATH=${top_srcdir}:${top_srcdir}/pylib:${top_builddir}/pylib; export PYTHONPATH;

TEST_EXTENSIONS = .py
PY_LOG_COMPILER = $(PYTHON)

TESTS = $(check_SCRIPTS)
EXTRA_DIST = $(check_SCRIPTS) HandlerMock.py
