#!/usr/bin/python

### pavel.jedlicka@akqa.com
### ./check_smb_shares -H 10.2.20.111 -l 'Client01, Client02, Departments, Documents, Transfer'

import sys, os, argparse

def check(host, args):
	STATUS = 0
	wanted = args.split()
	cmd = '/usr/bin/smbclient -U EMEA/emea.nagios%N1giosadmin! -L //'+host+'/ | awk \'{print $1}\''
	failed_list = ''
	try:
	   data = os.popen(cmd).read().strip().split("\n")
	   
      	   for item in wanted:
    		if item not in data:
        		failed_list += str(item) + ";"
			STATUS = 1
   	except:
            pass
	
	if STATUS != 0:
        	print "CRITICAL: Couldn't connect to share, wanted: '%s'" % failed_list
        	sys.exit(2)
        else:
        	print "OK: Everything looks fine"
        	sys.exit(0)


### GRAB ARGUMENTS FROM COMMAND LINE
def main(argv):
  	host = ''
  	parser = argparse.ArgumentParser(description='Check samba shares.')
  	parser.add_argument('-H','--host', help='File server IP address',required=True)
  	parser.add_argument('-l','--list', help="List of shares expected Eg. -l 'Share01, Share02'", required=True)
  	args = parser.parse_args()
  	host = args.host
  	wanted = args.list.replace(',','')
 
### DO CHECK ON ARGUMENTS   
  	check(host,wanted)

if __name__ == "__main__":
   	main(sys.argv[1:])

