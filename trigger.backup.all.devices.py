from trigger.netdevices import NetDevices
import os
import pwd
import grp
import subprocess
import socket
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

try:

	#Pull in SNMP credentials from file
	f = open('/etc/trigger/snmp_creds', 'r')
	snmpCred = [list(map(str,line.rstrip('\n').split(':'))) for line in f]

	def snmpSet(community, host, oid, setValue, setType):
		cmdGen = cmdgen.CommandGenerator()
		if setType is 'ipAddress':
			errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
				cmdgen.CommunityData(community),
				cmdgen.UdpTransportTarget((host, 161)),
				(oid, rfc1902.IpAddress(setValue))
				#(cmdgen.MibVariable('SNMPv2-MIB', 'sysORDescr', 1), 'new comment')
			)
		elif setType is 'integer':
			errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
				cmdgen.CommunityData(community),
				cmdgen.UdpTransportTarget((host, 161)),
				(oid, rfc1902.Integer(setValue))
				#(cmdgen.MibVariable('SNMPv2-MIB', 'sysORDescr', 1), 'new comment')
			)
		elif setType is 'string':
			errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
				cmdgen.CommunityData(community),
				cmdgen.UdpTransportTarget((host, 161)),
				(oid, rfc1902.OctetString(setValue))
				#(cmdgen.MibVariable('SNMPv2-MIB', 'sysORDescr', 1), 'new comment')
			)

		# Check for errors and print out results
		if errorIndication:
			#print(errorIndication)
			#return errorIndication
			pass
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBinds[int(errorIndex)-1] or '?'
					)
				)
			else:
				for name, val in varBinds:
					#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
					return val

	def snmpGet(community, host, oid):
		cmdGen = cmdgen.CommandGenerator()

		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
			cmdgen.CommunityData(community),
			cmdgen.UdpTransportTarget((host, 161)),
			oid
		)

		# Check for errors and print out results
		if errorIndication:
			#print(errorIndication)
			#return errorIndication
			pass
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBinds[int(errorIndex)-1] or '?'
					)
				)
			else:
				for name, val in varBinds:
					#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
					return val

	def snmpGetNext(community, host, oid):
		cmdGen = cmdgen.CommandGenerator()

		errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.nextCmd(
			cmdgen.CommunityData(community),
			cmdgen.UdpTransportTarget((host, 161)),
			oid
		)

		if errorIndication:
			#print(errorIndication)
			#return errorIndication
			pass
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
					)
				)
			else:
				for varBindTableRow in varBindTable:
					for name, val in varBindTableRow:
						#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
						return val

	dir = os.path.dirname('/var/data/network-backups/')
	nd = NetDevices()

	for device in nd:
		#create directories in TFTP server if necessary as xinetd tftp-server does not allow for directory creation.
		newdir = dir + "/" + nd[device].nodeName

		if not os.path.exists(newdir):
			os.makedirs(newdir)
			chowncmd = "/usr/bin/sudo chown nobody:nobody " + newdir
			process = subprocess.Popen(chowncmd, stdout=subprocess.PIPE, shell=True)
			(output, err) = process.communicate()
			#print output

		#not all the devices in netdevices.json have DNS records...working on creating them all.  Then this can be removed.
		try:
			devIP = socket.gethostbyname(nd[device].nodeName)
		except:
			devIP = '127.0.0.1'

		#check to see if device is responding to snmp at all, if so, continue the copy job on that host.
		if snmpGetNext(snmpCred[2][2], devIP, '1.3.6.1.2.1.1.5'):
			#delete the copy job on the router if there is a stale job
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.14.336', 6, 'integer')

			#set all variables and kick off copy job on router
			#Full CISCO-CONFIG-COPY-MIB can be found at https://supportforums.cisco.com/docs/DOC-1860
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.2.336', 1, 'integer') #copy protocol: tftp
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.3.336', 3, 'integer') #source file: startup-config = 3, running-config = 4
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.4.336', 1, 'integer') #destination file: network-file = 1
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.5.336', '172.16.206.244', 'ipAddress') #copy server address = IP address of TFTP server
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.6.336', 'network-backups/' + nd[device].nodeName + '/startup-config.txt', 'string') #copy file path on tftp server
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.14.336', 1, 'integer') #activate the copy job.

			#check job completion status
			jobStatus = snmpGetNext(snmpCred[2][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.10') #Get copy job status.
			while jobStatus == 2: 															#keep getting job status until it is no longer in progress and either suceeds or fails.
				jobStatus = snmpGetNext(snmpCred[2][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.10')
			if jobStatus != 3:
				print nd[device].nodeName, ': Copy Job Failed.  SNMP status = ', jobStatus
			else:
				print nd[device].nodeName, ': Copy Job Succeeded. SNMP status = ', jobStatus
			
			#delete the completed copy job
			snmpSet(snmpCred[3][2], devIP, '1.3.6.1.4.1.9.9.96.1.1.1.1.14.336', 6, 'integer') #destroy copy job after it is completed.
		else:
			print nd[device].nodeName, ': No SNMP Response From Host'

except KeyboardInterrupt:
	print '\nProcess killed by keyboard interrupt'
except:
	print 'Unspecified Error'