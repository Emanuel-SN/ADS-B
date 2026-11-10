
import os
import threading
import time

import config


FIELDS = ("flight", "alt", "gs", "track", "lat", "lon")
COLUMNS = ("time", "hex") + FIELDS
_lock = threading.Lock()
_latest = {}


def _record_from_line(line):
    """Turn one pipe-separated line into a record dictionary."""
    if not line.strip() or line.startswith("#"):
        return None
    values = line.rstrip("\r\n").split("|")
    if len(values) != len(COLUMNS):
        return None
    return dict(zip(COLUMNS, values))


def _clean(value):
    """Keep each record on one line and preserve the text separator."""
    value = "" if value is None else str(value)
    return value.replace("|", " ").replace("\n", " ").replace("\r", " ")


def _write_header(file):
    file.write("#" + "|".join(COLUMNS) + "\n")


def load_previous_values():
    """Restore each aircraft's last known values from history.txt."""
    if not config.HISTORY_FILE.exists():
        return

    with _lock, config.HISTORY_FILE.open(encoding="utf-8") as file:
        for line in file:
            row = _record_from_line(line)
            if row and row["hex"]:
                _latest[row["hex"]] = {field: row[field] for field in FIELDS}


def save_message(message):
    """Merge one SBS message into the plane record and append a text line."""
    hex_address = message["hex"]

    with _lock:
        values = _latest.setdefault(hex_address, {field: "" for field in FIELDS})
        for field in FIELDS:
            if message.get(field) not in (None, ""):
                values[field] = message[field]

        record = {
            "time": f"{time.time():.3f}",
            "hex": hex_address,
            **values,
        }
        is_new_file = (
            not config.HISTORY_FILE.exists()
            or config.HISTORY_FILE.stat().st_size == 0
        )
        with config.HISTORY_FILE.open("a", encoding="utf-8") as file:
            if is_new_file:
                _write_header(file)
            line = "|".join(
                _clean(record[column]) for column in COLUMNS
            )
            file.write(line + "\n")


def read_history():
    """Read the text history for serial transmission."""
    if not config.HISTORY_FILE.exists():
        return []

    records = []
    with _lock, config.HISTORY_FILE.open(encoding="utf-8") as file:
        for line in file:
            row = _record_from_line(line)
            if row:
                records.append(row)
    return records


def remove_old_rows(now=None):
    """Keep only text records within the configured number of days."""
    if config.KEEP_DAYS <= 0 or not config.HISTORY_FILE.exists():
        return

    now = time.time() if now is None else now
    cutoff = now - config.KEEP_DAYS * 86400
    temp_file = config.HISTORY_FILE.with_suffix(".tmp")

    with _lock:
        latest = {}
        with config.HISTORY_FILE.open(encoding="utf-8") as source:
            with temp_file.open("w", encoding="utf-8") as target:
                _write_header(target)
                for line in source:
                    row = _record_from_line(line)
                    if not row:
                        continue
                    try:
                        keep = float(row["time"]) >= cutoff
                    except ValueError:
                        keep = True

                    if keep:
                        target.write(line if line.endswith("\n") else line + "\n")
                        latest[row["hex"]] = {field: row[field] for field in FIELDS}

        os.replace(temp_file, config.HISTORY_FILE)
        _latest.clear()
        _latest.update(latest)
