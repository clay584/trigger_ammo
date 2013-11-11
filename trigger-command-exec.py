#!/usr/bin/env python2
'''
Description:        This script when used with Trigger will run a command across all Cisco devices and return the output.  most of this script comes straight from the Trigger documentation.
'''
__author__ = 'Clay Curtis'
__license__ = 'MIT License'
__contact__ = 'clay584 with gmail'
__version__ = 1.0


from trigger.cmds import Commando
from trigger.netdevices import NetDevices
import simplejson as json
import re

nd = NetDevices()


class CommandExec(Commando):
    vendors = ['cisco']
    commands = ['show clock']

    def to_cisco(self, device, commands=None, extra=None):
        print "Sending %r to %s" % (self.commands, device)
        return self.commands

    def from_cisco(self, results, device):
        if device.nodeName not in self.results:
            self.results[device.nodeName] = {}

        for cmd, result in zip(self.commands, results):
            self.results[device.nodeName][cmd] = result

if __name__ == '__main__':
    
    device_list = []
    for i in nd:
        dev = nd[i]
        device_list.append(str(dev.nodeName))
    
    commandExec = CommandExec(devices=device_list)
    commandExec.run() # Commando exposes this to start the event loop

    print '\nResults:'
    strout = commandExec.results
    for key, value in commandExec.results.iteritems():
        newvalue = re.sub(r"^[^:]+ '(.*)'}$",r"\1",str(value))
        print newvalue
    
