#!/usr/bin/env python

import argparse
import sys
import logging as log

from modules import ipsecsa, configsync, pathmonitor, registeredip, dynaddrgroup, utils 


def main():
    args = parse_args(sys.argv[1:])
    check = args.func.create_check(args)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Nagios check for Palo Alto firewalls')
    parser.add_argument('-H', '--host',
                            help='PaloAlto Server Hostname',
                            required=True)
    parser.add_argument('-T', '--token',
                            help='Generated Token for REST-API access',
                            required=True)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    # Sub-Parser for command 'ipsecsa'.
    parser_ipsecsa = subparsers.add_parser('ipsecsa', help='Check ipsec sa for VPN tunnel.')
    parser_ipsecsa.add_argument('-t', '--tunnel',
                            help='Tunnel Name',
                            required=False)
    parser_ipsecsa.set_defaults(func=ipsecsa)
    
    # Sub-Parser for command 'configsync'
    parser_configsync = subparsers.add_parser('configsync', help='Check if config is synchronized.')
    parser_configsync.set_defaults(func=configsync)

    # Sub-Parser for command 'pathmonitor'
    parser_pathmonitor = subparsers.add_parser('pathmonitor', help='Check static route path monitoring.')
    parser_pathmonitor.set_defaults(func=pathmonitor)

    # Sub-Parser for command 'registeredip'
    parser_registeredip = subparsers.add_parser('registeredip', help='Check registered ip tag.')
    parser_registeredip.set_defaults(func=registeredip)

     # Sub-Parser for command 'dynamicaddressgroup'
    parser_dynaddrgroup = subparsers.add_parser('dynaddressgroup', help='Check dynamic address group <name>.')
    parser_dynaddrgroup.add_argument('-g', '--groupname', help='Dynamic Group Name', required=True)
    parser_dynaddrgroup.set_defaults(func=dynaddrgroup)

    return parser.parse_args(args)


if __name__ == '__main__':
    main()