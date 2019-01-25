import json
import requests, urllib3
import logging as log


def _isjson(myjson):
	""" Return true is JSON is valid and is not empty """

	try:
		json_object = json.loads(json.dumps(myjson))
		if json_object:
			return True
		else:
			return False
		print
	except ValueError:
		return False

def _hasValidParams(myjson):
	""" Return true if payload contains a valid cisco command  """

	if 'error' in myjson:
		return False	
	else:
		return True


def nagios_msg(exitcode, message=''):
	""" Exit gracefully with exitcode and (optional) message 
	Nagios exit codes:
	0	OK
	1	WARNING
	2	CRITICAL
	3	UNKNOWN
	"""

	log.debug('Exiting with status {0}. Message: {1}'.format(exitcode, message))

	if message:
		print(message)
	exit(exitcode)

def reader(username, password, url, cmd, timeout = 10):
	""" Create a connection and return response if valid """

	headers = {'content-type': 'application/json-rpc'}
	payload = [{"jsonrpc": "2.0",
              "method": "cli",
              "params": {"cmd": cmd,
                        "version": 1},
              "id": 1}
              ]

	try:
		urllib3.disable_warnings()
		requests.packages.urllib3.disable_warnings()
		response = requests.post(url, data=json.dumps(payload), headers=headers, auth=(username, password), verify=False, timeout=timeout).json()

		if _isjson(response):
			if _hasValidParams(response):
				return response
			else:
				nagios_msg(3, "cisco command: " + response['error']['message'] )
		else:
			nagios_msg(3, "invalid or empty JSON object")

	except requests.exceptions.RequestException as e:
		nagios_msg(3, "Connection error: " + str(e))


