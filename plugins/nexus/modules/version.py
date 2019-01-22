## Cisco: show version

from utils import nagios_msg, reader

def create_check(args):
    """ Specify command and define check logic """

    cmd = "show version"
    host = args.host
    url = "https://"+host+"/ins"
    username = args.username
    password = args.password
 
    response = reader(username, password, url, cmd)
    
    kick_start_image = response['result']['body']['kickstart_ver_str']
    chassis_id = response['result']['body']['chassis_id']
    hostname = response['result']['body']['host_name']
    uptime = (str(response['result']['body']['kern_uptm_days']) + " days " + 
              str(response['result']['body']['kern_uptm_hrs']) +  " hours " +
              str(response['result']['body']['kern_uptm_mins']) + " minutes")
    last_reload_reason = response['result']['body']['rr_reason']
    output = "Uptime: {0}, Chassis: {1}, Hostname: {2}, Software version: {3}, Last reload reason: {4}".format(uptime , chassis_id, hostname, kick_start_image, last_reload_reason)

    if args.warning:
      m_runtime = (int(response['result']['body']['kern_uptm_days']) * 1440) + (int(response['result']['body']['kern_uptm_hrs']) * 60) + int(response['result']['body']['kern_uptm_mins'])
      
      if int(m_runtime) < int(args.warning):
        nagios_msg(1, "Warning: " + output)
      else:
        nagios_msg(0, "OK: " + output)
    else:
      nagios_msg(0, "OK: " + output)


    

