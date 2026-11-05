#!/bin/bash
cd "$(dirname "$0")"

# stop any leftover copy so the dongle isn't busy
pkill dump1090 2>/dev/null
sleep 1

# folder that vanishes on reboot
mkdir -p /dev/shm/adsb

# start the decoder in the background
./dump1090/dump1090 --write-json /dev/shm/adsb --quiet > /dev/null 2>&1 &
DUMP_PID=$!

# when this script ends (Ctrl+C or crash), stop the decoder too
trap 'echo "stopping..."; kill $DUMP_PID 2>/dev/null' EXIT

# give dump1090 a few seconds to open the dongle and write the first file
sleep 3

# run your program in the foreground
python3 main.py