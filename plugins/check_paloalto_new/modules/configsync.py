## Check IPsec SA on PaloAlto Next Gen Firewall

from .utils import nagios_msg, XMLreader
from bs4 import BeautifulSoup as bs

def create_check(args):
    cmd = '<show><high-availability><all></all></high-availability></show>'
    xml = XMLreader(args.host, args.token, cmd)
    result = xml.read()

    status = result.find('running-sync')
    status = status.get_text()
    config = result.find('running-sync-enabled')
    config = config.get_text()


    if config == "yes":
        if status == "not synchronized":
            nagios_msg(1,'Warning, PA Not Synchronized')
        else:
            nagios_msg(0,'Sync OK')
    else:
        nagios_msg(3,'Sync is Not Enabled')
