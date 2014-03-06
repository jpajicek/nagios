#!/bin/bash
## pavel.jedlicka@akqa.com

result_Ok=1
result_Warning=0
result_exit_Ok=0
result_exit_Warning=1
result_exit_Critical=2
result=0

ipaddr=$1

id='username'
pass='password'

rm -f /tmp/cisco-ntp-$ipaddr.txt

/usr/bin/expect <<EOF > /dev/null
set timeout 10

spawn ssh -o StrictHostKeyChecking=no $id@$ipaddr
expect "Password: "
send "$pass\n"

expect "#$"
log_file /tmp/cisco-ntp-$ipaddr.txt
send -- "sh ntp status | include Clock|NTP\n"
expect "#$"
send -- "sh clock\n"
expect "#$"
log_file
expect "#$"
send "exit\r"

EOF

result=`cat /tmp/cisco-ntp-$ipaddr.txt | grep -w synchronized | wc -l`

if [ $result -eq $result_Warning ]; then
	echo `cat /tmp/cisco-ntp-$ipaddr.txt | awk 'FNR == 2 {print}'`
	echo `cat /tmp/cisco-ntp-$ipaddr.txt | awk 'FNR == 4 {print}'`
	exit $result_exit_Warning
fi

if [ $result -eq $result_Ok ]; then
	echo -e " OK - `cat /tmp/cisco-ntp-$ipaddr.txt | awk 'FNR == 2 {print}'` \n `cat /tmp/cisco-ntp-$ipaddr.txt | awk 'FNR == 4 {print}'`"
	exit $result_exit_Ok
fi


