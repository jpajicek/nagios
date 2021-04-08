# eigrp.py, Cisco: show ip eigrp neighbors

import shelve
from modules.utils import nagios_msg, reader

def create_check(args):
	""" Specify command and define check logic """
	vrf_name = args.vrf
	cmd = "show ip eigrp neighbors vrf "+vrf_name
	host = args.host
	url = "https://"+host+"/ins"
	username = args.username
	password = args.password
	count = args.count
 	
	response = reader(username, password, url, cmd)
	check_result(count, eigrpNeighbors(response))

def check_result(expected_count, data):
	cache = shelve.open('/tmp/eigrp.db')
	current_count = int(data[0])
	neighbor_list = data[1]
	expected_count = int(expected_count) 
	cache['current_status'] = []
	cache['ok_status'] = []
	diff = []

	if expected_count == current_count:
		cache['ok_status'] = neighbor_list
		cache.close()
		nagios_msg(0, 'OK: EIGRP peers OK - Found {0} neighbors '.format(current_count))
	if expected_count < current_count: 
		cache['current_status'] = neighbor_list
		diff = [ peer for peer in cache['current_status'] if peer not in cache['ok_status']]
		cache.close()
		nagios_msg(1, 'Warning: Total number of neighbors is {0}. Found new EIGRP adjacency with -> {1}'.format(current_count, diff))
	if expected_count > current_count: 		
		cache['current_status'] = neighbor_list
		diff = [ peer for peer in cache['ok_status'] if peer not in cache['current_status']]
		cache.close()
		nagios_msg(1, 'Warning: Total number of neighbors is {0}. Lost EIGRP adjacency with -> {1}'.format(current_count, diff))

def eigrpNeighbors(response):
	""" Return eigrp peers + count """
	status = []
	raw_data = response['result']['body']['TABLE_asn']['ROW_asn']['TABLE_vrf']['ROW_vrf']['TABLE_peer']
 
	for peer in raw_data:
		peers = raw_data[peer]

	count = len(peers)	

	for item in peers:
		status.append({"peer": str(item['peer_ipaddr']), "interface": str(item['peer_ifname'])})

	return count, status
