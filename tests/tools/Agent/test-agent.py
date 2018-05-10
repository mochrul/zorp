#!/usr/bin/env python2.7

############################################################################
##
## Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
## Copyright (c) 2015-2017 BalaSys IT Ltd, Budapest, Hungary
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

from TestAgentImpl import TestAgentImpl
import sys,os

try:
    os.system("rm -f log")
    i = TestAgentImpl(sys.stdin, sys.stdout)
    while i.dispatch_command():
        i.log("dispatch new command")
        pass
        i.log("get out of msg loop")
except (EOFError, IOError, KeyboardInterrupt):
    pass