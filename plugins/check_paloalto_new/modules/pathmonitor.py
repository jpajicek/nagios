## Check static route path monitoring  on PaloAlto Next Gen Firewall

from utils import nagios_msg, XMLreader

def create_check(args):
    cmd = '<show><routing><path-monitor></path-monitor></routing></show>'
    data = XMLreader(args.host, args.token, cmd)
    result = data.read()
    GetPathMonitorStatus(result)


def GetPathMonitorStatus(result):
    try:
    	status = result.find('pathmonitor-status').get_text().strip()
    except Exception as e:
	 nagios_msg(3,'UNKNOWN:'
                        ' Oops! Path monitoring not configured -  %s' % e )
    if status == 'Up':
	nexthop = result.nexthop.string
	destination = result.destination.string
	nagios_msg(0,'OK:'
                        ' Path monitoring for %s via %s is UP' % (destination,nexthop) )
    elif status == 'Down':
	nagios_msg(1,'WARNING:'
                        ' Path monitoring is DOWN' )
    elif "Up Hold" in status:
	nagios_msg(1,'WARNING:'
                        ' Path monitoring is %s' % status )
    else:
	nagios_msg(3,'UNKNOWN:'
                        ' Oops! Something went wrong' )

