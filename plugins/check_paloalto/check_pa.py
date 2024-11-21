import argparse
import sys
import logging as log

from modules import ipsecsa, configsync, pathmonitor, registeredip, dynaddrgroup, license, utils 

def main():
    args = parse_args(sys.argv[1:])
    check = args.func.create_check(args)

def parse_args(args):
    parser = argparse.ArgumentParser(description='Nagios check for Palo Alto firewalls')
    parser.add_argument('-H', '--host', help='PaloAlto Server Hostname', required=True)
    parser.add_argument('-T', '--token', help='Generated Token for REST-API access', required=True)

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Define command configurations
    commands = [
        ('ipsecsa', 'Check ipsec sa for VPN tunnel.', ipsecsa, [('-t', '--tunnel', 'Tunnel Name', False)]),
        ('configsync', 'Check if config is synchronized.', configsync, []),
        ('pathmonitor', 'Check static route path monitoring.', pathmonitor, []),
        ('registeredip', 'Check registered ip tag.', registeredip, []),
        ('dynaddrgroup', 'Check dynamic address group <name>.', dynaddrgroup, [('-g', '--groupname', 'Dynamic Group Name', True)]),
        ('license', 'Check license status', license, [('-d', '--days', 'Expiring in days', False)])
    ]

    # Add subparsers dynamically
    for cmd_name, cmd_help, cmd_func, cmd_args in commands:
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_help)
        cmd_parser.set_defaults(func=cmd_func)
        
        for arg_short, arg_long, arg_help, arg_required in cmd_args:
            cmd_parser.add_argument(arg_short, arg_long, help=arg_help, required=arg_required)

    return parser.parse_args(args)

if __name__ == '__main__':
    main()