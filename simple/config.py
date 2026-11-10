"""The settings most people may want to change."""

from pathlib import Path

FOLDER = Path(__file__).resolve().parent

# Local antirez/dump1090 SBS feed
SBS_HOST = "127.0.0.1"
SBS_PORT = 30003

# Plain text history file and retention
HISTORY_FILE = FOLDER / "history.txt"
HISTORY_SEPARATOR = "|"
KEEP_DAYS = 30  # 0 means keep forever

# GPIO request and serial output
GPIO_PIN = 23
SERIAL_PORT = "/dev/serial0"
SERIAL_BAUD = 115200

# Change this tuple to choose the serial fields and their order.
SERIAL_COLUMNS = ("time", "hex", "flight", "alt", "gs", "track", "lat", "lon")
SERIAL_SEPARATOR = "|"
SERIAL_END_MARKER = "END"
