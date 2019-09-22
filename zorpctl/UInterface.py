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

from __future__ import print_function
import sys
import zorpctl.utils

class UInterface(object):
    def __init__(self):
        pass

    @staticmethod
    def _printMessage(message, file=None):
        if zorpctl.utils.isSequence(message):
            for msg in message:
                print(str(msg), file=file)
        else:
            print(str(message), file=file)

    @staticmethod
    def informUser(message):
        UInterface._printMessage(message)

    @staticmethod
    def warnUser(message):
        UInterface._printMessage(message, sys.stderr)
