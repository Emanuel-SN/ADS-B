#!/bin/bash
cd "$(dirname "$0")"

pkill dump1090 2>/dev/null
sleep 1

# antirez/dump1090 streams decoded SBS messages on TCP port 30003
./dump1090/dump1090 --net > /dev/null 2>&1 &
DUMP_PID=$!
trap 'echo "stopping..."; kill "$DUMP_PID" 2>/dev/null' EXIT

sleep 3
python3 simple_version/main.py
