## Show registered IP tags on PaloAlto Next Gen Firewall

from .utils import nagios_msg, XMLreader

def create_check(args):
    cmd = '<show><object><registered-ip><tag></tag></registered-ip></object></show>'
    data = XMLreader(args.host, args.token, cmd)
    result = data.read()


def GetResult():
    pass