#!/usr/bin/python

### pavel.jedlicka@akqa.com
### Deps
### apt-get install python-pip
### pip install spur

import sys
import optparse
import paramiko
import time
import re

data = ''
cmd = 'sh dhcpd statistics | include Automatic bindings'

def parse_opts():
   
    desc = 'A python plugin for Nagios to monitor ASA dhcp pool bindings.'

    usage = "check_asa_shun.py -H <ip> -l <username> -p <password> -w 240 -c 250"

    parser = optparse.OptionParser(description=desc, usage=usage)

    # optparse automatically sets up --help for us
    parser.add_option('-H', '--hostname', default='localhost',
        help='The hostname or ip of target system.')
    parser.add_option('-l', '--logname',
        help='The login/username on remote host. (defaults to current user)')
    parser.add_option('-p', '--password',
        help='Authentication password for user at remote host')
    parser.add_option('-w', '--warning', default=240,
        help='number of bindings for warning')
    parser.add_option('-c', '--critical', default=250,
        help='number of bindings for critical')
    return parser.parse_args()

def output(arg,warning,critical):
    tmp=int(re.search(r'\d+', arg).group())
    result=int(tmp)
    warning=int(warning)
    critical=int(critical)
   
    if result >= critical:
       print "CRITICAL: DHCP leases - %s | bindings=%s" % (result,result)
       sys.exit(3)
    elif (result >= warning) and (result < critical):
       print "WARNING: DHCP leases - %s | bindings=%s" % (result,result)
       sys.exit(2)
    else: 
       print "OK: DHCP leases - %s | bindings=%s" % (result,result)
       sys.exit(0)


def main():
    opts = parse_opts()
    host = opts[0].hostname
    user = opts[0].logname
    pswd = opts[0].password

    try: 
       ssh = paramiko.SSHClient()
       ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       ssh.connect(host, username=user, password=pswd, look_for_keys=True)
       ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       shell = ssh.invoke_shell()    
       shell.send('en\n')
       time.sleep(1)
       data = shell.recv(9999)	
   
       shell.send(''+pswd+'\n')
       time.sleep(1)
       data = shell.recv(9999)
      
       shell.send(''+cmd+'\n')
       time.sleep(1)
       data = shell.recv(9999)
       output(data,opts[0].warning,opts[0].critical) 
    except paramiko.AuthenticationException as error:
    	print error

if __name__ == "__main__":
    main()

