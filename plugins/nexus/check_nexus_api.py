#!/usr/bin/env python

import argparse
import sys
import logging as log

from modules import version, vpc, fex


def main():

    """Nagios plugin for Nexus switches using NX-API. NX-API CLI is an enhancement to the Cisco Nexus Series CLI system.
    See Cisco's documentation programming guides for additional details and how to enable NX-API feature.
    https://www.cisco.com/c/en/us/support/switches/nexus-9000-series-switches/products-programming-reference-guides-list.html
    """
    
    args = parse_args(sys.argv[1:])
    check = args.func.create_check(args)


def parse_args(args):
    
    """ Parse arguments """

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-H', '--host',
                            help='Device hostname or ip address',
                            required=True)
    parser.add_argument('-U', '--username',
                            help='Device username',
                            required=True)

    parser.add_argument('-P', '--password',
                            help='Device password',
                            required=True)
                            
    subparsers = parser.add_subparsers()
    subparsers.required = True

    # Sub-Parser for command 'version'.
    parser_version = subparsers.add_parser('version', help='Show device details (show version)')
    parser_version.add_argument('-w', '--warning', help='Generate warning if uptime is below this threshold (optional, in minutes)', required=False)
    parser_version.set_defaults(func=version)

    # Sub-Parser for command 'vpc'.
    parser_vpc = subparsers.add_parser('vpc',  help='Show vpc brief')
    parser_vpc.add_argument('-o', '--option', choices=['domain', 'portchannel'], required=False)
    parser_vpc.add_argument('-r', '--role', help='Expect VPC role to be primary or secondary, eg. vpc -o domain -r primary (optional)', default='', required=False)
    parser_vpc.set_defaults(func=vpc)

    # Sub-Parser for command 'fex'.
    parser_fex = subparsers.add_parser('fex', help='Show fex details')
    parser_fex.set_defaults(func=fex)

    return parser.parse_args(args)

if __name__ == '__main__':
    main()
