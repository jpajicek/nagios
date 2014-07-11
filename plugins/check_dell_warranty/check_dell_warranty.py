#!/usr/bin/python



### pavel.jedlicka@akqa.com

### Deps: apt-get install python-suds python-setuptools python-pynetsnmp

### This plugin is to check warranty using DELL service tag read via SNMP



import sys, datetime
import netsnmp, argparse, suds

def getServiceTag(hst,com):
    	oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.674.10892.1.300.10.1.11'))
    	res = netsnmp.snmpwalk(oid, Version = 2, DestHost=hst, Community=com)
    	return res

def get_warr(svctag):
        url = "http://xserv.dell.com/services/assetservice.asmx?WSDL"
        client = suds.client.Client(url)
        res=client.service.GetAssetInformation('12345678-1234-1234-1234-123456789012', 'dellwarrantycheck', svctag)
 
        hdrdata=res['Asset'][0]['AssetHeaderData']
        ent=res['Asset'][0]['Entitlements'][0]
 
        shipped=hdrdata['SystemShipDate']
        warrs=[]
        for i in ent:
                if i==None:
                        continue
                warrs.append(i['EndDate'])
	 
        warrs.sort()
        endwarranty=warrs[-1]
        daysleft=endwarranty - datetime.datetime.now()
        return (shipped.strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%Y-%m-%d"), endwarranty.strftime("%Y-%m-%d"), daysleft.days)
 

def main(argv):
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
         	print "You must provide snmp community or dell service tag, see help -h"
		sys.exit(3)
	if args.community != 0 and args.tag == 0:
		tag=getServiceTag(host,commstring)       
		(shipped, currdate, endw, daysleft)=get_warr(tag[0])	
	elif args.community == 0 and args.tag != 0:
		(shipped, currdate, endw, daysleft)=get_warr(tag)
		
	if int(daysleft) < int(args.warning):
		print "WARNING: Warranty ends in %s days , Warranty ends: %s, Server was shipped on: %s (y-m-d)" % (str(daysleft),str(endw),str(shipped))
                sys.exit(1)
        else:
                print "OK: Warranty days left: %s , Warranty ends: %s, Server was shipped on: %s (y-m-d)" % (str(daysleft),str(endw),str(shipped))
                sys.exit(0)

  	

if __name__ == "__main__":
   	main(sys.argv[1:])

