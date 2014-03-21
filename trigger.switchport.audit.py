#This script will audit switchports to make sure access ports have portfast turned on.
#It will also output cmd files which are remediation scripts that can later be run against all devices.

from trigger.netdevices import NetDevices
from ciscoconfparse import CiscoConfParse

dataDir = '/var/data/network-backups/'
nd = NetDevices()

cfgDiffs = []

def standardizeInt(parsed_config):
	interfaces = parsed_config.find_lines('^interface.+?thernet')
	for i in interfaces:
		famobj = CiscoConfParse(parsed_config.find_children(i, exactmatch=True))
		if (famobj.find_lines('switchport mode access')):
			if (not famobj.find_lines('spanning-tree portfast')):
				cfgDiffs.append(i)
				cfgDiffs.append(" spanning-tree portfast")

for i in nd:
	try:
		orig_config = str(dataDir) + str(nd[i].nodeName) + '/startup-config.txt'
		parsed_config = CiscoConfParse(orig_config)
		cfgDiffs.append('conf t')
		standardizeInt(parsed_config)
		cfgDiffs.append('end')
		cfgDiffs.append('wr mem')
		#parsed_config.commit()
		#parsed_config.save_as(dataDir + nd[i].nodeName + '/startup-config.txt.new')
		newCfg = open(str(dataDir) + str(nd[i].nodeName) + '/startup-config.txt.cmd', 'w')
		for line in cfgDiffs:
			#print line
			newCfg.write(str(line) + '\n')
		del cfgDiffs[0:len(cfgDiffs)]
		newCfg.close()
	except Exception, e:
		#print 'File ' + dataDir + nd[i].nodeName + '/startup-config.txt does not exist...skipping'
		print e
