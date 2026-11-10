from pathlib import Path

FOLDER = Path(__file__).resolve().parent

SBS_HOST = "127.0.0.1"
SBS_PORT = 30003

HISTORY_FILE = FOLDER / "history.txt"
KEEP_DAYS = 30

GPIO_PIN = 23
SERIAL_PORT = "/dev/serial0"
SERIAL_BAUD = 115200
