#!/bin/bash
# Author: jpajicek@gmail.com

WARN="$1"
CRIT="$2"

TOTAL=$(/usr/bin/lsof -u gearman | wc -l)


if [ $# -lt 2 ]; then
        echo "Usage: $0 <warning> <critical>"
        exit 3
fi

if [ "$TOTAL" -lt "$WARN" -a "$TOTAL" -lt "$CRIT" ]; then 
  echo "OK: Total number of open sockets is $TOTAL | sockets=$TOTAL"
  exit 0
fi

if [ "$TOTAL" -ge "$WARN" -a "$TOTAL" -lt "$CRIT" ]; then 
  echo "WARNING: Total number of open sockets is $TOTAL | sockets=$TOTAL"
  exit 1
fi

if [ "$TOTAL" -ge "$CRIT" -a "$TOTAL" -gt "$WARN" ]; then
  echo "CRITICAL: Total number of open sockets is $TOTAL | sockets=$TOTAL"
  exit 2
else
  echo "Unknown:"
  exit 3
fi
