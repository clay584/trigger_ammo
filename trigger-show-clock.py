from trigger.cmds import Commando
from trigger.netdevices import NetDevices
import simplejson as json
import re

nd = NetDevices()


class ShowClock(Commando):
    """Execute 'show clock' on a list of Cisco devices."""
    vendors = ['cisco']
    commands = ['show clock']

    def to_cisco(self, device, commands=None, extra=None):
        """Passes the commands as-is to the device"""
        print "Sending %r to %s" % (self.commands, device)
        return self.commands

    def from_cisco(self, results, device):
        """Capture the command output and move on"""
        if device.nodeName not in self.results:
            self.results[device.nodeName] = {}

        # Store each command and its result for this device
        for cmd, result in zip(self.commands, results):
            self.results[device.nodeName][cmd] = result

if __name__ == '__main__':
    device_list = ['sar-mas-1.sar.net.jtax.com', 'sar-mas-2.sar.net.jtax.com']
    """
    device_list = []
    for i in nd:
        dev = nd[i]
        device_list.append(str(dev.nodeName))
    """
    showclock = ShowClock(devices=device_list)
    showclock.run() # Commando exposes this to start the event loop

    print '\nResults:'
    strout = showclock.results
    #print(json.dumps(strout, sort_keys=True, indent=4 * ' '))
    for key, value in showclock.results.iteritems():
        newvalue = re.sub(r"^[^:]+ '(.*)'}$",r"\1",str(value))
        print newvalue
    
