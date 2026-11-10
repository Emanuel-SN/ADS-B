#!/bin/bash
cd "$(dirname "$0")"

# Stop a leftover decoder so it does not hold the SDR dongle.
pkill dump1090 2>/dev/null
sleep 1

# Start the local antirez/dump1090 decoder.
./dump1090/dump1090 --net > /dev/null 2>&1 &
DUMP_PID=$!
trap 'echo "stopping..."; kill "$DUMP_PID" 2>/dev/null' EXIT

sleep 3
python3 main.py
