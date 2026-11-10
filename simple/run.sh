pkill dump1090
sleep 3

./dump1090/dump1090 --net &

sleep 3
python3 main.py

pkill dump1090