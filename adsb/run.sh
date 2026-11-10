pkill dump1090
sleep 3

./dump1090/dump1090 --net &

trap 'pkill dump1090' EXIT

sleep 3
python3 main.py