#!/usr/bin/env python2.7

############################################################################
##
## Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
## Copyright (c) 2015-2018 BalaSys IT Ltd, Budapest, Hungary
##
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##
############################################################################

import tempfile
import datetime
import unittest, os
from zorpctl.ProcessAlgorithms import DetailedStatusAlgorithm, ProcessStatus

class TestDetailedStatusAlgorithm(unittest.TestCase):

    def setUp(self):
        (self.test_uptime_file_fd, self.test_uptime_file_name) = tempfile.mkstemp(prefix='test_proc_uptime_file')
        os.write(self.test_uptime_file_fd, '19534.16 66241.85')
        os.close(self.test_uptime_file_fd)

        (self.test_stat_file_fd, self.test_stat_filename) = tempfile.mkstemp(prefix='test_proc_stat_file')
        os.write(self.test_stat_file_fd,
                 "cpu  677042 37221 447831 6575990 23683 4 1743 0 0 0" \
                 "cpu0 198740 7613 139162 1584199 4778 3 729 0 0 0" \
                 "cpu1 166518 10310 106719 1651103 6142 0 334 0 0 0" \
                 "cpu2 157808 9493 102157 1668239 4922 0 347 0 0 0" \
                 "cpu3 153976 9804 99791 1672447 7840 0 332 0 0 0" \
                 "intr 97534152 43 11472 0 0 0 0 0 2 1 0 0 0 0 0 0 0 88194 2 304 285 0 0 128079 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 405590 %s" \
                 "ctxt 194770779" \
                 "btime 1367748435" \
                 "processes 32903" \
                 "procs_running 2" \
                 "procs_blocked 0" \
                 "softirq 17765007 0 3342173 3318 444082 127922 0 9080 3165220 1741954 8931258')" % (701 * "0 "))
        os.close(self.test_stat_file_fd)

        self.algorithm = DetailedStatusAlgorithm()
        self.algorithm.uptime_filename = self.test_uptime_file_name
        self.algorithm.stat_file = open(self.test_stat_filename, 'r')

        self.procinfo = {
            "majflt": "22",
            "cutime": "0",
            "endcode": "1",
            "vsize": "295555072",
            "wchan": "18446744073709551615",
            "tpgid": "-1",
            "sigcatch": "89659",
            "cstime": "0",
            "pid": "1572",
            "_dummyzero": "4",
            "cminflt": "0",
            "session": "1572",
            "comm": "(zorp)",
            "stime": "32",
            "startstack": "0",
            "sigignore": "16777216",
            "startcode": "1",
            "processor": "3",
            "tty_nr": "0",
            "cmajflt": "0",
            "rss": "3120",
            "priority": "20",
            "ppid": "1571",
            "minflt": "3288",
            "itrealvalue": "0",
            "kstkesp": "0",
            "rlim": "18446744073709551615",
            "nswap": "0",
            "utime": "46",
            "exit_signal": "17",
            "pgrp": "1572",
            "state": "S",
            "flags": "4202816",
            "starttime": "2466",
            "kstkeip": "0",
            "blocked": "0",
            "cnswap": "0",
            "signal": "0",
            "nice": "0"
        }

    def tearDown(self):
        os.remove(self.test_uptime_file_name)
        os.remove(self.test_stat_filename)

    def test_detailed_status(self):
        status = ProcessStatus("test")
        status.reload_timestamp = 1367664125
        status.policy_file = "/etc/zorp/policy.py"
        expected_result =('policy: file=/etc/zorp/policy.py, loaded=%s' % (datetime.datetime.fromtimestamp(status.reload_timestamp)) +
                 '\ncpu: real=0:0.780000, user=0:0.460000, sys=0:0.320000\n' +
                 'memory: vsz=288628kB, rss=12480kB'
        )
        chop_len = len('started at: yyyy-mm-dd xx:xx:xx.xxxxxx\n')
        #must chop started at part because of now and uptime calculations
        #no better solution yet
        result = self.algorithm.assembleDetails(status, self.procinfo, self.algorithm.getJiffiesPerSec())
        self.assertEquals(result[chop_len:], expected_result)


if __name__ == '__main__':
    unittest.main()
