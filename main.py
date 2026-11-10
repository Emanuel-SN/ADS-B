import time
import threading

from gpiozero import DigitalInputDevice

import config
import storage
from adsb_source import parse_sbs_message, stream_sbs_lines
from sender import Sender


sender = Sender()
request = DigitalInputDevice(config.ENABLE_PIN, pull_up=False)


def archive_worker():
    """Read decoded messages continuously and save aircraft history."""
    for line in stream_sbs_lines():
        try:
            message = parse_sbs_message(line)
            if message:
                storage.append_message(message)
        except Exception as error:
            print("archive error:", error)


def main():
    storage.prune_history()
    storage.load_latest_records()
    threading.Thread(target=archive_worker, daemon=True).start()

    was_high = False
    last_prune = time.time()
    try:
        while True:
            now = time.time()
            if now - last_prune >= storage.PRUNE_EVERY_SECONDS:
                removed = storage.prune_history(now)
                if removed:
                    print(f"pruned {removed} expired history rows")
                last_prune = now

            is_high = bool(request.value)
            if is_high and not was_high:
                sender.send_history(storage.read_history_rows())
            was_high = is_high
            time.sleep(0.02)
    finally:
        request.close()


if __name__ == "__main__":
    main()
