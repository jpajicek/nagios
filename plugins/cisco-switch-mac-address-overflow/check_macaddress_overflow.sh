#!/bin/bash
# Requirements apt-get install sshpass

result_Ok=0
result_Critical=1
result_exit_Ok=0
result_exit_Warning=1
result_exit_Critical=2
result=0

ipaddr=$1

LOGFILE="/tmp/cisco-macoverflow-$ipaddr.txt"

id='emea.nagios'
pass='N1giosadmin!'

rm -f $LOGFILE

sshpass -p$pass ssh -o StrictHostKeyChecking=no $id@$ipaddr "sh mac address-table count | i Available:" > $LOGFILE

result=$(cat $LOGFILE | grep 'Available: [0]' | wc -l)
free=$(cat $LOGFILE | awk '{print $NF}')

if [ $result -eq $result_Critical ]; then
        printf "%s\n" "CRITICAL: Mac-address overflow - available is ${free}" "|mac_free=${free}"
        exit $result_exit_Critical
else
	printf "%s\n" "OK: Mac-addresses available is ${free}" "|mac_free=${free}"
        exit $result_exit_Ok 
fi

