#get computer names and desc from AD, add to object group script, send to ncm

import csv
from orionsdk import SwisClient
import shutil
import os
from os import path
import re
from time import sleep
from datetime import datetime

#open the text file to dump the ASA commands for local reference.
asacommands = open("asacommands.txt","w")

#get our timestamp to use in the commands
now = datetime.now()
now_str = now.strftime("%Y/%m/%d %H:%M")

#create list of commands to send to ASA
asa_cmd_list = []

#add conf t to the start of the command list
asa_cmd_list.append("conf t\n")

#open list of computers
computers = open("computers.csv","a")

#add lines to asa_cmd_list for each computer
with open('computers.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
           line_count +=1
        DNSHostname = (f'{row["DNSHostname"]}')
        Description = (f'{row["Description"]}')
        #print(DNSHostname)
        obj_net = 'object network AD_' + DNSHostname + '\n fqdn ' + DNSHostname + '\n description Added by Script - ' + Description + '\n'
        #print(obj_net)
        asa_cmd_list.append(obj_net)
        obj_grp = 'object-group network AD-Computers-Object-Group\n network-object object AD_' + DNSHostname + ' \n'
        #print(obj_grp)
        asa_cmd_list.append(obj_grp)
        line_count += 1


#add command to update the object-group desc to include time
asa_cmd_list.append("object-group network AD-Computers-Object-Group\ndesc Last Updated by Script on " + now_str +"\n")

#add escape and wr to the end of the command list
asa_cmd_list.append("end\nwr\n")

orion_cmd = ' ' .join(asa_cmd_list)
print(orion_cmd)

#write everything to a file just for future reference
asacommands.writelines(orion_cmd)
asacommands.close()

#Orion API connection details
npm_server = 'server name'
username = 'orion username'
password = 'orion password'
swis = SwisClient(npm_server, username, password)

#open the csv of IPs for devices, for every ip in the CSV, lookup the Node ID of that device
#create and execute the command job for each device. Each job has a unique Transfer ID that's compiled of the NodeID+OrionAPI username+action.
#The job tranfers from this script can be found in the SolarWinds DB in the Cirrus.TransferQueue table. 
#print outputs here are only for terminal viewing.
with open('orion-devices.csv', mode='r') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	line_count = 0
	for row in csv_reader:
		if line_count == 0:
			line_count +=1
		ip_addr = (f'{row["deviceip"]}')
		data = swis.query('SELECT NodeID FROM Cirrus.Nodes WHERE AgentIP = @ip', ip=ip_addr)['results']
		nodeId = data[0]['NodeID']
		transferId = '{{{0}}}:{1}:ExecuteScript'.format(nodeId, username)
		print(ip_addr)
		print(transferId)
		swis.invoke('Cirrus.ConfigArchive', 'Execute', [nodeId], orion_cmd, username)
		line_count +=1

#This is here because it's cute.
print("Done")