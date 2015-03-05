#!/bin/bash
# Author: pavel.jedlicka@akqa.com


URL="$1"
LOGIN="$2"
WARN="$3"
CRIT="$4"


if [ $# -lt 4 ]; then
        echo "Usage: $0 URL <username:password> <warning> <critical>"
        exit 3
fi

LICENSE=$(/usr/bin/curl -s -u $LOGIN -X GET $URL | grep -ioE "[0-9,]{1,5} signed up currently" | grep -ioE "[0-9,]{1,5}" | tr -d ,)


if [ "$LICENSE" == "" ]; then 
	echo "UNKNOWN: Could read the number of users signed up"
 	exit 3
fi

if [ "$WARN" -ge "$CRIT" ]; then 
        echo "UNKNOWN: WARNING must be less then CRITICAL thresholds"
        exit 3
fi

if [ "$LICENSE" -lt "$WARN" -a "$LICENSE" -lt "$CRIT" ]; then
        echo "OK: Total number of users signed up is $LICENSE | used=$LICENSE"
  	exit 0
fi

if [ "$LICENSE" -ge "$WARN" -a "$LICENSE" -lt "$CRIT" ]; then
        echo "WARNING: Total number of users signed up is $LICENSE | used=$LICENSE"
        exit 1
fi

if [ "$LICENSE" -ge "$CRIT" -a "$LICENSE" -gt "$WARN" ]; then
        echo "CRITICAL: Total number of users signed up is $LICENSE | used=$LICENSE"
        exit 3
else
        echo "UNKNOWN: unknown error occurred"
        exit 3
fi

