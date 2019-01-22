## Cisco: show vpc 

import re
from utils import nagios_msg, reader

def create_check(args):
	""" Specify command and define check logic """

	cmd = "show vpc brief"
	host = args.host
	url = "https://"+host+"/ins"
	username = args.username
	password = args.password
 	option = str(args.option)

 	response = reader(username, password, url, cmd)

	vpc_peer_status = response['result']['body']['vpc-peer-status']
	vpc_peer_status_reason = response['result']['body']['vpc-peer-status-reason']
	vpc_peer_keepalive_status = response['result']['body']['vpc-peer-keepalive-status']
	vpc_peer_consistency_status = response['result']['body']['vpc-peer-consistency-status']
	vpc_type_2_consistency_status = response['result']['body']['vpc-type-2-consistency-status']
	vpc_role = response['result']['body']['vpc-role']
	
	### Group options
	consistency_params = {'vpc_peer_status_reason':vpc_peer_status_reason,'vpc_peer_consistency_status':vpc_peer_consistency_status, 'vpc_type_2_consistency_status':vpc_type_2_consistency_status}
	peer_status_params = {'vpc_peer_status': vpc_peer_status, 'vpc_peer_keepalive_status': vpc_peer_keepalive_status, 'vpc_role': vpc_role, 'vpc_role_expected': args.role }

	vpc_params = {'peerStatus': peer_status_params, 'isSuccess': consistency_params }

	if option == "portchannel":
		status = vpcStatus(response)
		if bool(status['inconsistent']):
			nagios_msg(1, 'Warning: vPC portchannel(s) in inconsistent state: {0}'.format(status['inconsistent']))
		else:
			nagios_msg(0, 'OK: No consistency errors found - vPC portchannel(s) in UP state: {0}'.format(status['active']))
	else:
		long_msg = vpcDomainStatus(response)
		status = consistencyCheck(vpc_params)

		if bool(status['inconsistent']):
			nagios_msg(1, 'Critical: {0} -- Details: {1}'.format(str(status['inconsistent']), long_msg))
		else:
			nagios_msg(0, 'OK: {0}'.format(long_msg))


def vpcDomainStatus(response):
	""" Return summary of VPC domain status (exclude VPC table) """

	summary_status = ""
	for key, value in response['result']['body'].items():
	
		if not any(re.findall(r'TABLE_[vpc|peerlink]|vpc-end', key)):
			status = str(key) + ": " + str(value) + ", "
			summary_status = summary_status + status 

	return summary_status
	

def vpcStatus(response):
	""" Return list of failed and active VPC's """

	vpc_failed = []
	vpc_active = []

	for vpc in response['result']['body']['TABLE_vpc']['ROW_vpc']:
		vpc_status = vpc['vpc-consistency-status']
		vpc_name = vpc['vpc-ifindex']
		vpc_state = vpc['vpc-port-state']
		
		if str(vpc_status) == 'INVALID':  ## and str(vpc_state) == '1':  # Only consider ports in UP state. (Can inconsistent be in UP state (1)?)
			vpc_failed.append(str(vpc_name))

		if str(vpc_status) == 'SUCCESS':
			vpc_active.append(str(vpc_name))

	return {"inconsistent":vpc_failed, "active":vpc_active} 


def consistencyCheck(params):
	""" Return items with consistency failures """

	failed = {}

	if params['peerStatus']['vpc_peer_status'] != "peer-ok":
		failed['vpc_peer_status'] = str(params['peerStatus']['vpc_peer_status'])
		failed['vpc_peer_status_reason'] = str(params['peerStatus']['vpc_peer_keepalive_status'])
	
	if params['peerStatus']['vpc_role_expected'] and (params['peerStatus']['vpc_role_expected'] != params['peerStatus']['vpc_role']):
		failed['vpc_role'] = str(params['peerStatus']['vpc_role']) + ' - EXPECTED: ' + str(params['peerStatus']['vpc_role_expected'])

	for key,value in params['isSuccess'].items():
		if str(value) != "SUCCESS":
			failed[key] = str(value)
		
	return {'inconsistent': failed}




