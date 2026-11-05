import time, threading
from gpiozero import DigitalInputDevice

import config, storage
from adsb_source import read_aircraft
from tracker import Tracker
from sender import Sender

tracker = Tracker(storage.load_state())
sender = Sender()
request = DigitalInputDevice(config.ENABLE_PIN, pull_up=False)

def worker():
    """Background: read, merge, log, save."""
    last_save = 0
    while True:
        rows = tracker.update(read_aircraft())
        storage.append_history(rows)
        if time.time() - last_save > config.SAVE_S:
            storage.save_state(tracker.export())
            last_save = time.time()
        time.sleep(config.POLL_S)

threading.Thread(target=worker, daemon=True).start()

was_high = False
while True:
    if request.value and not was_high:
        sender.send(tracker.snapshot())
    was_high = bool(request.value)
    time.sleep(0.02)