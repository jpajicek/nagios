#!/usr/bin/env python

import sys, logging
import requests,json
import argparse

base_url = 'https://api.meraki.com/api/v1/'
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
        print(str(statuscode))
        _nagios_msg(3, 'Connection Error: {0}'.format(str(statuscode)))


def _reader(url):
    headers = {
         'Accept': "*/*",
         'x-cisco-meraki-api-key': format(str(apikey)),
         'Content-Type': 'application/json'
     }
    requests.packages.urllib3.disable_warnings()
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
    
def getdevicestatus(**params):
    
    d_online = []
    d_offline = []
    d_dormant = []
    d_alerting = []

    orgid = getorgid()
    devices = params.get('devices')

    for device in devices:
        name = device['name']
        serial = device['serial']
        #geturl = '{0}/networks/{1}/devices/{2}/uplink'.format(str(base_url), str(netid),str(serial))
        geturl = '{0}/organizations/{1}/devices/statuses?serials[]={2}'.format(str(base_url), str(orgid),str(serial))
        data = _reader(geturl)
        for key in data:
            status = key['status']
        if str(status) == 'online':
            d_online.append(str(name))
        if str(status) == 'offline':
            d_offline.append(str(name))
        if str(status) == 'alerting':
            d_alerting.append(str(name))
        if str(status) == 'dormant':
            d_dormant.append(str(name))
        #print(f'{name}: {status}')
    return { "online":d_online, "offline":d_offline, "dormant": d_dormant, "alerting": d_alerting }           


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
    status = getdevicestatus(devices=devices)
    
    if bool(status['offline']):  
        _nagios_msg(2, 'Critical: {0} Offline device(s): {1}'.format(len(status['offline']),str(status['offline'])))
    elif bool(status['alerting']):  
        _nagios_msg(1, 'Warning: {0} Alerting device(s): {1}'.format(len(status['alerting']),str(status['alerting'])))
    else:
        _nagios_msg(0, 
            f"OK: Let's dance, you are under surveillance - {len(status['online'])} Online device(s): {status['online']} | \n Dormant devices: {status['dormant']}")
    


if __name__ == '__main__':
    main()
