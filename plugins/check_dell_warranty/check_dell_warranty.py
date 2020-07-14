#!/usr/bin/python


### pavel.jedlicka@akqa.com + jonny.ford@akqa.com
### Deps: apt-get install python-suds python-setuptools python-pynetsnmp
### This plugin is to check warranty using DELL service tag read via SNMP

import sys, datetime
import netsnmp
import argparse, suds, requests, json, urllib3

client_id = 'l75128021f1a1149d7b673082fb4bafb20'
client_secret =  '6d37c4c648ce49158732862d01277a6c'


def getAuthToken():
	url = 'https://apigtwb2c.us.dell.com/auth/oauth/v2/token'
	client_data = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret }
	try:
		response = requests.post(url, verify=False, data=client_data)
		response.raise_for_status()
	except requests.exceptions.RequestException as e:
		print ("Error - {0}".format(e))
		sys.exit(3)
	data = json.loads(response.text)
	token = data['access_token']
	return token

def getServiceTag(hst,com):
	oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.674.10892.1.300.10.1.11'))
	res = netsnmp.snmpwalk(oid, Version = 2, DestHost=hst, Community=com)
	if str(res) != "()":
		return res
	else:
		print ("Couldn't read snmp value {0}".format(res))
		sys.exit(3)

def get_warr(svctag):
	shorturl = "https://apigtwb2c.us.dell.com/PROD/sbil/eapi/v5/asset-entitlements"
	auth_token = getAuthToken()
	url = shorturl+"?servicetags="+svctag
	try:
		response = requests.get(url, verify=False, headers={"Authorization":"Bearer " + auth_token})
		response.raise_for_status()
	except requests.exceptions.RequestException as e:
		print ("Couldn't read from Dell site: {0}".format(e))
		sys.exit(3)

	data = json.loads(response.text)
	if data != []:
		warranties = data[0]['entitlements']
		long_msg = []
		all_end_dates = []
		for warranty in warranties:
			all_end_dates.append(warranty['endDate'])  
			warranty_enddate = warranty['endDate']
			#item = 'Entitlement: '+str(warranty['serviceLevelDescription'])+', Expires: '+str(datetime.datetime.strptime(warranty['endDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date())
			item = 'Entitlement: '+str(warranty['serviceLevelDescription'])+', Expires: '+str(datetime.datetime.strptime(warranty_enddate[:12], '%Y-%m-%dT%H').date())
			long_msg.insert(0, item) 
		shipped = data[0]['shipDate']
		shipped = datetime.datetime.strptime(shipped, '%Y-%m-%dT%H:%M:%SZ').date()
		shipped_str = shipped.strftime("%Y-%m-%d")
		end_date =  max(all_end_dates)
		end_date = datetime.datetime.strptime(end_date[:12], '%Y-%m-%dT%H')
		end_date_str = end_date.strftime("%Y-%m-%d")
		daysleft = end_date - datetime.datetime.now()
		daysleft_str = daysleft.days
		now_str = datetime.datetime.now().strftime("%Y-%m-%d")
		return(shipped_str, now_str, end_date_str, daysleft_str, long_msg)
	else:
		print ("Received empty response from Dell, exiting ...")
		sys.exit(3)

def main(argv):
	urllib3.disable_warnings()
	requests.packages.urllib3.disable_warnings()
	host = ''
	parser = argparse.ArgumentParser(description='Check dell warranty plugin for Nagios')
	parser.add_argument('-H','--host', help='Dell server IP address',required=True)
	parser.add_argument('-C','--community', help='SNMP v2 community string',default=0)
	parser.add_argument('-T','--tag', help='DELL Service Tag',default=0)
	parser.add_argument('-W','--warning', help='Warning in days left (defaut 30)', default=30)
	args = parser.parse_args()

	host = args.host
	commstring = args.community	
	tag = args.tag

	if args.community == 0 and args.tag == 0:
		print ("You must provide snmp community or dell service tag, see help -h")
		sys.exit(3)
	if args.community != 0 and args.tag == 0:
		tag=getServiceTag(host,commstring)       
		(shipped, currdate, endw, daysleft, long_msg)=get_warr(tag[0])	
	elif args.community == 0 and args.tag != 0:
		(shipped, currdate, endw, daysleft,long_msg)=get_warr(tag)

	if int(daysleft) < int(args.warning):
		print ("WARNING: Warranty ends in {0} days, Expires: {1}, Server was shipped on: {2} (Y-M-D), Details: {3}".format(daysleft,endw,shipped,long_msg))
		sys.exit(1)
	else:
		print ("OK: Warranty days left: {0}, Expires: {1}, Server was shipped on: {2} (Y-M-D), Details: {3}".format(daysleft,endw,shipped,long_msg))
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv[1:])

