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
import re


def make_dns(hostname, interface, ip_address):
    #print hostname, interface, ip_address
    interface_name = ''
    host = hostname.split('.')
    if 'Ten' in interface:
        interface_name = re.sub(r'([0-9]+)/([0-9]+)',r'te\1-\2',interface)
    elif 'Gig' in interface:
        interface_name = re.sub(r'([0-9]+)/([0-9]+)',r'ge\1-\2',interface)
    elif 'Fast' in interface:
        interface_name = re.sub(r'([0-9]+)/([0-9]+)',r'fa\1-\2',interface)
    elif 'Port-channel' in interface:
        interface_name = re.sub(r'Port-channel([0-9]+)',r'po\1-\2',interface)
    elif 'Vlan' in interface:
        interface_name = re.sub(r'Vlan([0-9]+)',r'vl\1',interface)
    elif 'ethernet' in interface:
        interface_name = re.sub(r'ethernet([0-9]+)',r'e\1',interface)
    else:
        pass

    print 'dnscmd.exe sarad005.jtax.com /RecordAdd jtax.com ' + interface_name + '-' + host[0] + '.' + host[1] + ' A ' + ip_address

def parse_results(cmdOutput):
    for key, value in cmdOutput.iteritems():
        output_lines = str(value).split(r'\n')
        for i, line in enumerate(output_lines):
            if i == 0:
                pass
            elif 'unassigned' in line:
                pass
            elif 'administratively down' in line:
                pass
            elif 'up' in line:
                parsed_items = line.split()
                make_dns(key, parsed_items[0], parsed_items[1])
            else:
                pass


nd = NetDevices()


class CommandExec(Commando):
    vendors = ['cisco']
    commands = ['show ip interface brief']

    def to_cisco(self, device, commands=None, extra=None):
        print "Sending %r to %s" % (self.commands, device)
        return self.commands

    def from_cisco(self, results, device):
        if device.nodeName not in self.results:
            self.results[device.nodeName] = {}

        for cmd, result in zip(self.commands, results):
            self.results[device.nodeName][cmd] = result

if __name__ == '__main__':
    

    #device_list = ['pdc-bar-1.net.jtax.com']
    device_list = []
    for i in nd:
        dev = nd[i]
        device_list.append(str(dev.nodeName))
    
    commandExec = CommandExec(devices=device_list)
    commandExec.run() # Commando exposes this to start the event loop

parse_results(commandExec.results)
