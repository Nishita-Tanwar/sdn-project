import json
import urllib2
import copy
import sys
import os
import time
import re
import urllib
import requests
hashset=set([])
count=1

#function to add static flow to block the host
def addStaticFlow(switch_id,destination_ip):
	static_flow_url='http://localhost:8080/wm/staticflowpusher/json'
	global count
	count+=1
	global hashset
	if destination_ip in hashset:
		return
	hashset.add(destination_ip)
	#setting body for HTML POST request for setting static flow for destination_ip
	obj='{"switch": "00:00:00:00:00:00:00:02","name":"flow-mod-'+str(count)+'", "cookie":"0", "priority":"32768", "eth_type":"0x0800", "ipv4_dst":"'+str(destination_ip)+'", "active":"true", "actions":"set_ip_ttl=0"}'
	obj=json.loads(obj)
	response= requests.post(static_flow_url, data=json.dumps(obj))
	print 'limiting flow to host ', str(destination_ip)
	

#function to call addstatflow flow value exceeded the threshold
def checkThreshold(topKey,destination_ip):
	devices_url='http://localhost:8080/wm/device/'
	response=urllib2.urlopen(devices_url).read()
	device=json.loads(response)
	switch_id='00:00:00:00:00:00:00:02'
	
	addStaticFlow(switch_id,destination_ip)
	
source_set=set([])

#finding all the Datasources in the network
def findDatasource():
	data_sources='http://localhost:8008/flows/json'
	response=urllib2.urlopen(data_sources)
	global source_set
	source=json.loads(response.read())
	for entry in source:
		ipadd=entry['flowKeys'].split(",")
		if ipadd[1]=='10.0.0.1' or ipadd[1]=='10.0.0.2':
			source_set.add(entry['dataSource'])

#function to track flows of all host trying to flood external internet
def getValues(threshold_value):
	events_url='http://localhost:8008/events/json'
	events_response=urllib2.urlopen(events_url).read()
	findDatasource()
	obj=[]
	for entry in source_set:
		flows_url='http://localhost:8008/metric/127.0.0.1/'+str(entry)+'.flows/json'
		response = urllib2.urlopen(flows_url).read()
		obj+=json.loads(response)

	max1={}
	val1=0
	max2={}
	val2=0
	top_key_map={}
	for _list in obj:
		if 'topKeys' not in _list:
			continue 
		for topKey in _list['topKeys']:
			value=topKey['value']
			ip=topKey['key'].split(',')
			threshold=''
			if "0.0.0.0" in ip:
				continue
			if value > threshold_value:
				checkThreshold(topKey,ip[0])
				threshold='exceeded threshold'
			print 'source: ',ip[0] ,' | ', 'destination: ',ip[1],' | ', 'value: ', value, ' | ', threshold
	


flag=True
if len(sys.argv)>1:
	threshold=sys.argv[1]
else:
	threshold=4000 # setting default threshold value to 4000
while(flag):
	os.system('clear')
	getValues(threshold) # calling getValues function to track flows
	time.sleep(2)
