#!/usr/bin/python

### pavel.jedlicka@akqa.com
### Deps: python-paramiko
### apt-get install python-paramiko
### Version 0.1

import sys
import optparse
import paramiko
import time
import re

data = ''
cmd = 'sh shun'

def parse_opts():
   
    desc = 'A python plugin for Nagios to monitor ASA shun list via ssh.'

    usage = "check_asa_shun.py -H <ip> -l <username> -p <password> -e '1.1.1.1, 2.2.2.2'"

    parser = optparse.OptionParser(description=desc, usage=usage)

    # optparse automatically sets up --help for us
    parser.add_option('-H', '--hostname', default='localhost',
        help='The hostname or ip of target system.')
    parser.add_option('-l', '--logname',
        help='The login/username on remote host. (defaults to current user)')
    parser.add_option('-p', '--password',
        help='Authentication password for user at remote host')
    parser.add_option('-e', '--exclude', default='',
        help='Ip addresses to exclude.')
    return parser.parse_args()


def filter_ips(data):
    regex=re.compile("^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$")
    return [m.group(0) for l in data for m in [regex.search(l)] if m]

def output(arg,excl):

    data = arg.replace("0.0.0.0",'').strip().split()
    exclude = excl.replace(',','').split()
    tmp = filter_ips(data)
    result = list(set(tmp) - set(exclude))

    if len(result) == 0:
       print 'OK: Threat detection'
       sys.exit(0)
    else: 
       print "WARNING: Threat detection shunned IP - %s" % result
       sys.exit(1)


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
       output(data,opts[0].exclude) 
       print data
    except paramiko.AuthenticationException as error:
    	print error

if __name__ == "__main__":
    main()

