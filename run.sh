#!/bin/bash
cd "$(dirname "$0")"

# stop any leftover copy so the dongle isn't busy
pkill dump1090 2>/dev/null
sleep 1

# antirez/dump1090 streams decoded SBS data over TCP port 30003 with --net
./dump1090/dump1090 --net > /dev/null 2>&1 &
DUMP_PID=$!

# when this script ends (Ctrl+C or crash), stop the decoder too
trap 'echo "stopping..."; kill "$DUMP_PID" 2>/dev/null' EXIT

# give dump1090 time to open the dongle and start its network listener
sleep 3

# run your program in the foreground
python3 main.py
