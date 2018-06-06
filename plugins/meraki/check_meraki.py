#!/usr/bin/env python

import sys, logging
import requests,json
import argparse

base_url = 'https://api.meraki.com/api/v0/'
apikey = ''
netid = ''

def _setkey(key):   
    global apikey 
    apikey = key
    return apikey
    
def _isjson(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True

def _nagios_msg(exitcode, message=''):
    logging.debug('Exiting with status {0}. Message: {1}'.format(exitcode, message))
    if message:
        print(message)
    exit(exitcode)
    
def _returnhandler(statuscode, returntext):
    validreturn = _isjson(returntext)
    
    if validreturn:
        returntext = json.loads(returntext)
    else:
        _nagios_msg(3, 'HTTP:{0} - Failed to load JSON file'.format(str(statuscode)))

    if str(statuscode) == '200' and validreturn:
        return returntext
    else:
        print str(statuscode)
        _nagios_msg(3, 'Connection Error: {0}'.format(str(statuscode)))


def _reader(url):
    headers = {
         'x-cisco-meraki-api-key': format(str(apikey)),
         'Content-Type': 'application/json'
     }
    dashboard = requests.get(url, headers=headers)
    result = _returnhandler(dashboard.status_code, dashboard.text)
    return result
   
def getorgid():
    geturl = '{0}/organizations'.format(str(base_url))
    data = _reader(geturl)
    for key in data:
        return key['id']
     
def getdevicelist(netid):
    geturl = '{0}/networks/{1}/devices'.format(str(base_url), str(netid))
    result = _reader(geturl)
    return result
    
def getdevicestatus(devicelist, netid):
    d_failed = []
    d_active = []
    for device in devicelist:
        name = device['name']
        serial = device['serial']
        geturl = '{0}/networks/{1}/devices/{2}/uplink'.format(str(base_url), str(netid),str(serial))
        data = _reader(geturl)
        for key in data:
            status = key['status']
        if str(status) == 'Failed':
            d_failed.append(str(name))
        if str(status) == 'Active':
            d_active.append(str(name))
        #print '{0} ::::: {1}'.format(name,status)
    return {"failed":d_failed, "active":d_active}           


def parse_args(args):
    parser = argparse.ArgumentParser(description='Nagios check for Meraki Cameras')
    parser.add_argument('-N', '--netid',
                            help='Meraki Network ID',
                            required=True)
    parser.add_argument('-T', '--token',
                            help='Generated Token for Meraki REST-API access',
                            required=True)
    return parser.parse_args(args)
    

def main():
    args = parse_args(sys.argv[1:])
    _setkey(str(args.token))
    netid = str(args.netid)
   
    devices = getdevicelist(netid)
    result = getdevicestatus(devices, netid)
    
    if bool(result['failed']):  
        _nagios_msg(2, 'Critical: {0} Failed device(s): {1}'.format(len(result['failed']),str(result['failed'])))
    else:
        _nagios_msg(0, "OK: Let's dance, you are under surveillance - All {0} device(s) is online: {1}".format(len(result['active']),str(result['active'])))
    


if __name__ == '__main__':
    main()