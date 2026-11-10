"""Run the simple ADS-B recorder, GPIO trigger, and serial sender."""

import threading
import time

from gpiozero import DigitalInputDevice

import config
import storage
from adsb_source import messages
from sender import send_history


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
