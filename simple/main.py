
import threading
import time
import socket

from gpiozero import DigitalInputDevice

import config
import storage
from sender import send_history

def parse_message(line):
    """Pick the fields this project stores from one SBS MSG line."""
    columns = line.strip().split(",")
    if len(columns) < 16 or columns[0] != "MSG":
        return None

    hex_address = columns[4].strip().lower()
    if not hex_address:
        return None

    def field(index):
        return columns[index].strip() or None

    return {
        "hex": hex_address,
        "flight": field(10),
        "alt": field(11),
        "gs": field(12),
        "track": field(13),
        "lat": field(14),
        "lon": field(15),
    }


def messages():
    """Yield messages from local dump1090; retry if its connection drops."""
    while True:
        try:
            with socket.create_connection((config.SBS_HOST, config.SBS_PORT), 5) as sock:
                print(f"Connected to dump1090 at {config.SBS_HOST}:{config.SBS_PORT}")
                with sock.makefile("r", encoding="utf-8") as stream:
                    for line in stream:
                        message = parse_message(line)
                        if message:
                            yield message
            print("dump1090 stream closed; reconnecting shortly")
        except OSError as error:
            print("Waiting for dump1090:", error)
        time.sleep(2)


def save_messages():
    """Keep saving messages while the main loop watches the GPIO pin."""
    for message in messages():
        try:
            storage.save_message(message)
        except Exception as error:
            print("Could not save aircraft message:", error)


def main():
    config.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    storage.remove_old_rows()
    storage.load_previous_values()
    threading.Thread(target=save_messages, daemon=True).start()

    request = DigitalInputDevice(config.GPIO_PIN, pull_up=False)
    was_high = False
    last_cleanup = time.time()

    try:
        while True:
            now = time.time()
            if now - last_cleanup >= 300:
                storage.remove_old_rows(now)
                last_cleanup = now

            is_high = bool(request.value)
            if is_high and not was_high:
                send_history()
            was_high = is_high
            time.sleep(0.02)
    finally:
        request.close()


if __name__ == "__main__":
    main()
