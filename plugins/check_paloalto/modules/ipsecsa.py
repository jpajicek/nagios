## Check IPsec SA on PaloAlto Next Gen Firewall

from .utils import nagios_msg, XMLreader


def create_check(args):
    cmd = '<show><vpn><ipsec-sa><tunnel>%s</tunnel></ipsec-sa></vpn></show>' % (args.tunnel)
    data = XMLreader(args.host, args.token, cmd)
    result = data.read()
    ## print(result)
    IPsecSummary(result)


class IPsecSummary():
    def __init__(self, data):
        self.ipsec = data
        self.exists = data.ntun.string
        self.error = data.find_all('error')
        if (self.exists != '0' and self.error == []):
            gateway = data.gateway.string
            peerip = data.remote.string
            life = data.life.string
            nagios_msg(0,'OK: IPsec tunnel is UP,'
                        ' via gateway %s. SA lifetime %s seconds, peer IP %s' % (gateway,life,peerip) )
        elif (self.exists != '0' and self.error != []):
            error = data.error.string
            nagios_msg(1,'WARNING:'
                        ' %s' % (error) )
        if (self.exists == '0'):
            nagios_msg(2,'CRITICAL:'
                        ' IPsec tunnel doesn\'t exist')