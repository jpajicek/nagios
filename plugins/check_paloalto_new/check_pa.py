#!/usr/bin/python

import argparse
import sys
import logging as log

from modules import ipsecsa, utils 


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
                            required=True)
    parser_ipsecsa.set_defaults(func=ipsecsa)

    return parser.parse_args(args)


if __name__ == '__main__':
    main()
