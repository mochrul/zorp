############################################################################
##
## Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
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

"""<module internal="yes" />

"""

import os
import re
import socket

CORE_SESSION = "core.session"
CORE_DEBUG = "core.debug"
CORE_ERROR = "core.error"
CORE_POLICY = "core.policy"
CORE_MESSAGE = "core.message"
CORE_AUTH = "core.auth"
CORE_INFO = "core.info"
CORE_SUMMARY = "core.summary"

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LogSpecItem(object):
    def __init__(self, logspec_item):
        categories, verbosity = logspec_item.split(":")

        self._verbosity = int(verbosity)
        if self._verbosity < 0 or self._verbosity > 10:
            raise ValueError("verbosity is out of range")

        self._categories = categories.split(".")
        if len(self._categories) != 2:
            raise ValueError("category value is invalid")

    def is_log_enabled(self, log_tag, log_verbosity):
        log_tag = LogSpecItem(log_tag + ":" + str(log_verbosity))

        for category_num in range(2):
            if (self._categories[category_num] != "*" and
                self._categories[category_num] != log_tag._categories[category_num]):
                return False

        return log_tag._verbosity <= self._verbosity

class LogFilter(object):
    logspec_pattern = re.compile(r': (([a-z]+|\*)\.([a-z]+|\*))\(\d\): ')

    def __init__(self, verbosity, logspec):
        self._verbosity = verbosity
        self._logspec = []

        if logspec:
            for logspec_item in logspec.split(","):
                self._logspec.append(LogSpecItem(logspec_item))

        self._logspec.append(LogSpecItem("*.*:" + str(self._verbosity, )))

    def is_log_enabled(self, log_tag, log_verbosity):
        for logspec in self._logspec:
            if logspec.is_log_enabled(log_tag, log_verbosity):
                return True

        return False

    def filter(self, record):
        logspec_match = LogFilter.logspec_pattern.search(record.msg)
        if not logspec_match:
            raise ValueError("log message does not contain logspec")

        logspec = logspec_match.group(1)
        return self.is_log_enabled(logspec, record.levelno)

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        self._verbosity = verbosity


class Logger(object):
    def __init__(self):
        self._name = None
        self._pid = 0
        self._logger = None
        self._handler = None
        self._verbosity = 3

    @property
    def verbosity(self):
        return self._logfilter.verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        self._logfilter.verbosity = verbosity

    @property
    def use_syslog(self):
        return self._use_syslog

    def _setup_handler(self):
        if not self._logger:
            raise ValueError("logger not initialized")

        if self._handler:
            self._logger.removeHandler(self._handler)

        try:
            if self._use_syslog:
                new_handler = self.__get_syslog_handler()
            else:
                new_handler = self.__get_stderr_handler()
        except socket.error as e:
            self._handler = None
        else:
            self._handler = new_handler
            self._logger.addHandler(self._handler)

    @use_syslog.setter
    def use_syslog(self, use_syslog):
        self._use_syslog = use_syslog
        self._setup_handler()

    def init(self, name, verbosity=3, logspec="", use_syslog=True):
        self._name = name
        self._pid = os.getpid()
        self._verbosity = verbosity
        self._logfilter = LogFilter(verbosity, logspec)

        import logging
        self._logger = logging.getLogger(self._name)
        self._logger.addFilter(self._logfilter)
        self._logger.setLevel(-1)

        self.use_syslog = use_syslog

    def __get_syslog_handler(self):
        import logging.handlers
        handler = logging.handlers.SysLogHandler(address="/dev/log")
        return handler

    def __get_stream_handler(self, stream):
        import logging
        handler = logging.StreamHandler(stream)
        return handler

    def __get_stderr_handler(self):
        import sys
        return self.__get_stream_handler(sys.stderr)

    def format_log(self, sessionid, logclass, verbosity, fmt, args=None):
        if not sessionid:
            sessionid = "nosession"

        if args is not None:
            msg = fmt % args
        else:
            msg = fmt

        logmsg = "%s[%d]: %s(%d): (%s): %s" % (self._name, self._pid, logclass, verbosity, sessionid, msg)

        return logmsg

    def log(self, sessionid, logclass, verbosity, fmt, args=None):
        if not self._logger:
            raise ValueError("logger not initialized")

        if verbosity < 0 or verbosity > 10:
            raise ValueError("verbosity is out of range")

        if self._handler is None:
            self._setup_handler()

        if self._handler is not None:
            try:
                logmsg = self.format_log(sessionid, logclass, verbosity, fmt, args)
            except (ValueError, TypeError) as e:
                self._logger.log(3, self.format_log(sessionid, "core.error", 3, "Unable to format log message; error='{0}'".format(e)))
                logmsg = self.format_log(sessionid, logclass, verbosity, "%s", (fmt, ))

            self._logger.log(verbosity, logmsg)

class LoggerSingleton(Logger):
    __metaclass__ = Singleton

def log(sessionid, logclass, verbosity, msg, args=None):
    """
    <function maturity="stable">
      <summary>
        Function to send a message to the system log.
      </summary>
      <description>
        <para>
          This function can be used to send a message to the system log.
        </para>
      </description>
      <metainfo>
        <arguments>
          <argument>
           <name>sessionid</name>
           <type><string/></type>
           <description>The ID of the session the message belongs to.</description>
          </argument>
          <argument>
            <name>logclass</name>
            <type><string/></type>
            <description>Hierarchical log class as described in the <emphasis>zorp(8)</emphasis> manual page</description>
          </argument>
          <argument>
            <name>verbosity</name>
            <type><integer/></type>
            <description>Verbosity level of the message.</description>
          </argument>
          <argument>
            <name>msg</name>
            <type><string/></type>
            <description>The message text.</description>
          </argument>
          <argument>
            <name>args</name>
            <type><string/></type>
            <description>Optional printf-style argument tuple added to the message.</description>
          </argument>
        </arguments>
      </metainfo>
    </function>
    """
    LoggerSingleton().log(sessionid, logclass, verbosity, msg)
