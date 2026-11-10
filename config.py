import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Local TCP connection to antirez/dump1090; loopback keeps runtime local.
SBS_HOST = "127.0.0.1"
SBS_PORT = 30003
SBS_RETRY_SECONDS = 2

# Local archive
HISTORY_PATH = os.path.join(BASE, "history.csv")
HISTORY_RETENTION_DAYS = 30  # set to 0 to keep records indefinitely
HISTORY_FIELDS = ["flight", "alt", "gs", "track", "lat", "lon"]

# Serial output and GPIO trigger
SERIAL_PORT = "/dev/serial0"
BAUD = 115200
ENABLE_PIN = 23
SEND_DELAY_S = 0.05
REPLY_TIMEOUT_S = 3
