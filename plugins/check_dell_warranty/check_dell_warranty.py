#!/usr/bin/python


### pavel.jedlicka@akqa.com + jonny.ford@akqa.com
### Deps: apt-get install python-suds python-setuptools python-pynetsnmp
### This plugin is to check warranty using DELL service tag read via SNMP

import sys, datetime
import netsnmp
import argparse, suds, requests, json, urllib3

client_id = 'l7528378424872394723947'
client_secret =  '6d37c4c648393498394839999'


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
		shipped = data[0]['shipDate']
		shipped = datetime.datetime.strptime(shipped, '%Y-%m-%dT%H:%M:%SZ')
		warranties = data[0]['entitlements']
		end_date = warranties[0]['endDate']
		end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.999Z')
		daysleft = end_date - datetime.datetime.now()
		now = datetime.datetime.now()
		return(shipped.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), daysleft.days)
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
		(shipped, currdate, endw, daysleft)=get_warr(tag[0])	
	elif args.community == 0 and args.tag != 0:
		(shipped, currdate, endw, daysleft)=get_warr(tag)

	if int(daysleft) < int(args.warning):
		print ("WARNING: Warranty ends in {0} days , Warranty ends: {1}, Server was shipped on: {2} (y-m-d)".format(daysleft,endw,shipped))
		sys.exit(1)
	else:
		print ("OK: Warranty days left: {0} , Warranty ends: {1}, Server was shipped on: {2} (y-m-d)".format(daysleft,endw,shipped))
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv[1:])

