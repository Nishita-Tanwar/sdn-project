import urllib2
import requests
import json

#deleting the static flow from flood light
def deleteStaticFlow():
	static_flow_url='http://localhost:8080/wm/staticflowpusher/json' #url to give delete command to floodlight 
	get_flow_url='http://localhost:8080/wm/staticflowpusher/list/all/json' # Rest request to get all static flows present in network
	response=urllib2.urlopen(get_flow_url).read()
	flows=json.loads(response)
	flow_items=[]
	for key,val in flows.items():
		for v in val:
			flow_items+=v.keys()
	for flow in flow_items:
		obj={}
		obj["name"]=str(flow)
		print obj
		response = requests.delete(static_flow_url, data=json.dumps(obj))
		print response.text

deleteStaticFlow()
	
