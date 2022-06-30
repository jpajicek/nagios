## Get members of dynamic address group and alert if found any.

from .utils import nagios_msg, XMLreader

def create_check(args):
    cmd = f'<show><object><dynamic-address-group><name>{args.groupname}</name></dynamic-address-group></object></show>'
    data = XMLreader(args.host, args.token, cmd)
    result = data.read()
    GetResult(args.groupname, result)

def GetResult(group, data):
    result = []
    members = data.find_all('member-list')
    for member in members:
        for entry in member.find_all('entry'):
            result.append(entry['name'])
    if result == []:
        nagios_msg(0, 'OK: Nothing to see here')
    else:
        nagios_msg(1, f'WARNING: Found {len(result)} member(s) of {group} group - {result}')