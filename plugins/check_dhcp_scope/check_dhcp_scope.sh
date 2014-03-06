#! /bin/bash
# ##############################################################################
# check_dhcp_split_scope.sh - Nagios plugin
# This is a fork of DHCP plugin writen by Lars Michelsen <lars@vertical-visions.de>, http://nagios.larsmichelsen.com/check_dhcp_pool/
# This plugin checks status of split DHCP scope
# 2006-07-05 Version 0.2 lars@vertical-visions.de
# 2007-10-27 Version 0.3 lars@vertical-visions.de
# 2013-01-13 Version 0.4 Pavel.Jedlicka@akqa.com - Add split scope monitoring 

if [ $# -lt 3 ]; then
	echo "Usage: $0 <'server1;server2'> <community> <pool-ip> [<warn=10>] [<crit=5>]"
	echo "Example1: $0 '10.2.20.93,10.2.20.94' public 10.2.100.0 10 5"
	echo "Example2: $0 10.2.20.93 public 10.2.100.0 10 5"
	exit 3
fi

IP="$1"
COMMUNITY="$2"
POOL="$3"
WARN="$4"
CRIT="$5"
i=0

if [ ${#WARN} -lt 1 ]
then
	WARN=10
fi

if [ ${#CRIT} -lt 1 ]
then
	CRIT=5
fi

FREEOID=".1.3.6.1.4.1.311.1.3.2.1.1.3.$POOL"
USEDOID=".1.3.6.1.4.1.311.1.3.2.1.1.2.$POOL"

arr=$(echo $IP | tr "," "\n")

for SERVER in $arr
do

SNMP_RESULT=`snmpget -v 2c -c $COMMUNITY $SERVER $FREEOID`
 FREE[$i]=`echo $SNMP_RESULT|cut -d " " -f4`
SNMP_RESULT=`snmpget -v 2c -c $COMMUNITY $SERVER $USEDOID`
 USED[$i]=`echo $SNMP_RESULT|cut -d " " -f4`
let i+=1

sleep 3

done

if  [ "${FREE[1]}" == "" -o "${USED[1]}" == "" ]; then
 FREE[1]=0
 USED[1]=0
fi

FREETOTAL=`echo ${FREE[0]} + ${FREE[1]} |bc`
USEDTOTAL=`echo ${USED[0]} + ${USED[1]} |bc`

MAX=`echo "$FREETOTAL+$USEDTOTAL" |bc`
PERCFREE=`echo "$FREETOTAL*100/$MAX" |bc`
PERCUSED=`echo "$USEDTOTAL*100/$MAX" |bc`

#DEBUG: echo "FREE: $FREETOTAL USED: $USEDTOTAL MAX: $MAX PERC: $PERCFREE,$PERCUSED"

if [ "$FREETOTAL" -le "$WARN" -a "$FREETOTAL" -gt "$CRIT" ]; then
	echo -n "Warning: $FREETOTAL Addresses in pool $POOL free"
	RET=1
elif [ "$FREETOTAL" -le "$CRIT" ]; then
	echo -n "Critical: $FREETOTAL Addresses in pool $POOL free"
	RET=2
else
	echo -n "OK: $FREETOTAL Addresses of $MAX in pool $POOL free"
	RET=0
fi

# Performance-Data
echo " | ipAddressesFree=$FREETOTAL;$WARN;$CRIT;0;$MAX"
exit $RET
