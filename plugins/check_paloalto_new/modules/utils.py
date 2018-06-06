import logging as log
import requests
from bs4 import BeautifulSoup

def nagios_msg(exitcode, message=''):
    """ Exit gracefully with exitcode and (optional) message """

    log.debug('Exiting with status {0}. Message: {1}'.format(exitcode, message))

    if message:
        print(message)
    exit(exitcode)

class XMLreader():
    def __init__(self, host, token, cmd):
        self.host = host
        self.token = token
        self.cmd = cmd
        self.request_url = 'https://%s/api/?key=%s&type=op&cmd=%s' % (self.host, self.token, self.cmd)

    def read(self):
        requests.packages.urllib3.disable_warnings()
        req = requests.post(self.request_url, verify=False, timeout=10)
        if req.status_code != 200:
	    nagios_msg(3,'Expected status code: 200 (OK), returned'
                        ' status code was: %d' % req.status_code)
        soup = BeautifulSoup(req.content, "lxml-xml")
        result = soup.response['status']
        if result != 'success':
	    nagios_msg(3,'Request didn\'t succeed, result was %s'
                        ' % result')
        return soup

