# fex.py

import json
from utils import nagios_msg, reader

def create_check(args):
	""" Specify command and define check logic """

	cmd = "show fex detail"
	host = args.host
	url = "https://"+host+"/ins"	
	username = args.username
	password = args.password

	response = reader(username, password, url, cmd)
	
	status = fexStatus(response)
	long_msg = json.dumps(status).strip('{}')

	if bool(status['failed']):
		nagios_msg(1, 'Critical: {0}'.format(long_msg))
	if bool(status['failed_uplink']):
		nagios_msg(1, 'Warning: {0}'.format(long_msg))
	else:
		nagios_msg(0, 'OK: {0}'.format(long_msg))


def fexStatus(input):
	""" Return status of fabric extenders """

	raw_data = input['result']['body']['TABLE_fex_info']['ROW_fex_info']

	fex_failed = {}
	fex_active = {}
	uplink_active = []
	uplink_failed = []

	if type(raw_data) is dict:
		TABLE_fex_info = []
		TABLE_fex_info.append(raw_data)
	else:
		TABLE_fex_info = raw_data


	for fex in TABLE_fex_info:	
		fex_status = fex['fex_state']
		fex_descr = fex['descr']
		fex_model = fex['model']
		fex_serial = fex['serial']
	
		if fex_status == 'Online':
			fex_active[str(fex_descr)] = [ str(fex_model), str(fex_serial) ]
		else:
			fex_failed[str(fex_descr)] = [ str(fex_model), str(fex_serial) ]

		for port in fex['TABLE_fbr_state']['ROW_fbr_state']:
			port_name = port['fbr_index']
			port_state = port['fsm_state']
			if str(port_state) == 'Active':
				uplink_active.append(str(port_name))
			else:
				uplink_failed.append(str(port_name))

	return {"failed":fex_failed, "active":fex_active, "failed_uplink":uplink_failed, "active_uplink":uplink_active}



################### Test JSON response (multiple extenders) #######################
#
# Mock HTTP response (testing)
# url = "http://www.mocky.io/v2/5c4a2d64340000da092694bc"
# url = "http://www.mocky.io/v2/5c4a2cc134000062002694b6"
#
#	{
#		"jsonrpc":"2.0",
#			"result":{
#				"body":{
#					"TABLE_fex_info":{
#						"ROW_fex_info":[
#							{
#								"descr":"FEX0101",
#								"fex_state":"Online",
#								"model":"N2K-C2232TM-E-10",
#								"serial":"SSI204AAAA",
#								"TABLE_fbr_state":{
#								"ROW_fbr_state":[
#									{
#										"fbr_index":"Po4",
#										"fbr_oper_state":"Up",
#										"fsm_state":"Active"
#									},
#									{
#										"fbr_index":"Eth1/53/4",
#										"fbr_oper_state":"Up",
#										"fsm_state":"Active"
#									}
#								]
#							}
#							},
#							{
#								"descr":"FEX0102",
#								"fex_state":"Online",
#								"model":"N2K-C2232TM-E-10GE",
#								"serial":"SSI204E02HA",
#								"TABLE_fbr_state":{
#								"ROW_fbr_state":[
#									{
#										"fbr_index":"Po4",
#										"fbr_oper_state":"Up",
#										"fsm_state":"Active"
#									},
#									{
#										"fbr_index":"Eth1/53/4",
#										"fbr_oper_state":"Up",
#										"fsm_state":"Active"
#									}
#								]
#							}
#						}
#					]
#				}
#			}
#		},
#	"id":1
#	}

