import os

BASE = os.path.dirname(os.path.abspath(__file__))

# dump1090
JSON_PATH = "/dev/shm/adsb/aircraft.json"

# files
STATE_PATH = os.path.join(BASE, "tracks.json")
HISTORY_PATH = os.path.join(BASE, "history.csv")

# serial / GPIO
SERIAL_PORT = "/dev/serial0"
BAUD = 115200
ENABLE_PIN = 23

# timing (seconds)
POLL_S = 1          # read aircraft.json this often
SAVE_S = 5          # save tracks.json this often
STALE_S = 5         # ignore dump1090 entries not heard in this long
EXPIRE_S = 120      # forget planes not heard for this long
SEND_MAX_AGE = 60   # only send planes heard within this long
SEND_DELAY_S = 0.05 # pause between serial lines
REPLY_TIMEOUT_S = 3 # wait for DONE this long

# fields sent, in order, after the hex address
FIELDS = ["flight", "alt", "gs", "track", "lat", "lon"]