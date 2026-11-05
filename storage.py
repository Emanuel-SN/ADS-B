import json, csv, os
import config

def load_state():
    try:
        with open(config.STATE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_state(tracks):
    tmp = config.STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(tracks, f)
    os.replace(tmp, config.STATE_PATH)   # atomic, never half-written

def append_history(rows):
    if not rows:
        return
    new_file = not os.path.exists(config.HISTORY_PATH)
    with open(config.HISTORY_PATH, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time", "hex"] + config.FIELDS)
        w.writerows(rows)