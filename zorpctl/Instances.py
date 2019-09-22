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

from Zorp.InstancesConf import InstancesConf
from Zorp.Instance import Instance
from zorpctl.ProcessAlgorithms import (StartAlgorithm, StopAlgorithm,
                                LogLevelAlgorithm , DeadlockCheckAlgorithm,
                                GUIStatusAlgorithm, StatusAlgorithm,
                                ReloadAlgorithm, PidAlgorithm, SzigWalkAlgorithm,
                                DetailedStatusAlgorithm, AuthorizeAlgorithm,
                                StopSessionAlgorithm)
from zorpctl.CommandResults import CommandResultFailure

class ZorpHandler(object):

    @staticmethod
    def start(use_systemd=False):
        return ZorpHandler.callAlgorithmToAllInstances(StartAlgorithm(use_systemd))

    @staticmethod
    def force_start(use_systemd=False):
        algorithm = StartAlgorithm(use_systemd)
        algorithm.force = True
        return ZorpHandler.callAlgorithmToAllInstances(algorithm)

    @staticmethod
    def stop():
        return ZorpHandler.callAlgorithmToAllInstances(StopAlgorithm())

    @staticmethod
    def force_stop():
        algorithm = StopAlgorithm()
        algorithm.force = True
        return ZorpHandler.callAlgorithmToAllInstances(algorithm)

    @staticmethod
    def reload():
        return ZorpHandler.callAlgorithmToAllInstances(ReloadAlgorithm())

    @staticmethod
    def pids():
        return ZorpHandler.callAlgorithmToAllInstances(PidAlgorithm())

    @staticmethod
    def status():
        return ZorpHandler.callAlgorithmToAllInstances(StatusAlgorithm())

    @staticmethod
    def gui_status():
        return ZorpHandler.callAlgorithmToAllInstances(GUIStatusAlgorithm())

    @staticmethod
    def detailedStatus():
        return ZorpHandler.callAlgorithmToAllInstances(DetailedStatusAlgorithm())

    @staticmethod
    def authorize(behaviour, session_id, description):
        return ZorpHandler.callAlgorithmToAllInstances(AuthorizeAlgorithm(behaviour, session_id, description))

    @staticmethod
    def log(mode, value=None):
        return ZorpHandler.callAlgorithmToAllInstances(LogLevelAlgorithm(mode, value))

    @staticmethod
    def deadlockcheck(value=None):
        return ZorpHandler.callAlgorithmToAllInstances(DeadlockCheckAlgorithm(value))

    @staticmethod
    def szig_walk(root):
        return ZorpHandler.callAlgorithmToAllInstances(SzigWalkAlgorithm(root))

    @staticmethod
    def stop_session(session_id):
        return ZorpHandler.callAlgorithmToAllInstances(StopSessionAlgorithm(session_id))

    @staticmethod
    def findManullyStartedInstances():
        import glob, os, re, subprocess
        paths = glob.glob("/var/run/zorp/zorp-*.pid")
        instance_names = []
        for path in paths:
            path_splitted = re.split('[-\.]', os.path.basename(path))
            instance_names.append(path_splitted[1])
        for zorpctl_instances in InstancesConf():
            regex = re.compile(zorpctl_instances.process_name.split('#')[0] + r'#[0-9]*')
            instance_names = filter(lambda i: not regex.search(i), instance_names)
        instances = []
        for instance_name in instance_names:
            instances.append(Instance(name = instance_name, process_name = instance_name, number_of_processes = 1, manually_started = True))
        return instances

    @staticmethod
    def callAlgorithmToAllInstances(algorithm):
        result = []
        try:
            manually_started_instances = ZorpHandler.findManullyStartedInstances()
            for manually_started_instance in manually_started_instances:
                result.extend(InstanceHandler.executeAlgorithmOnInstanceProcesses(manually_started_instance, algorithm))
            for instance in InstancesConf():
                result.extend(InstanceHandler.executeAlgorithmOnInstanceProcesses(instance, algorithm))
            return result
        except Exception as e:
            return [CommandResultFailure(e.message)]

class InstanceHandler(object):

    @staticmethod
    def executeAlgorithmOnInstanceProcesses(instance, algorithm):
        results = []
        for i in range(0, instance.number_of_processes):
            if instance.manually_started:
                instance.process_num = ''
            else:
                instance.process_num = i
            algorithm.setInstance(instance)
            result = algorithm.run()
            result.msg = "%s: %s" % (instance.process_name, result.msg)
            results.append(result)

        return results

    @staticmethod
    def searchInstance(instance_name):
        instances = []
        try:
            manually_started_instances = ZorpHandler.findManullyStartedInstances()
            for manually_started_instance in manually_started_instances:
                if manually_started_instance.name == instance_name:
                    instances.append(manually_started_instance)
            for instance in InstancesConf():
                if instance.name == instance_name:
                    instances.append(instance)
            if instances:
                return instances
            else:
                return [CommandResultFailure("Instance {0} not found!".format(instance_name), instance_name)]
        except IOError as e:
            return [CommandResultFailure(e.message)]
