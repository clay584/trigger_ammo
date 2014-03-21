from trigger.netdevices import NetDevices
from trigger.cmds import Commando

nd = NetDevices()
devicelist = []

class ShowHostname(Commando):
	vendors = ['cisco']
	commands = ['show run | inc hostname']

if __name__ == '__main__':
	for i in nd:
		devicelist.append(nd[i].nodeName)
	showhostname = ShowHostname(devices=devicelist)
	showhostname.run()

	print showhostname.results