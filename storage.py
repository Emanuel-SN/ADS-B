import csv
import os
import threading
import time

import config


CSV_COLUMNS = ["time", "hex"] + config.HISTORY_FIELDS
PRUNE_EVERY_SECONDS = 300
_lock = threading.Lock()
_latest_by_hex = {}


def load_latest_records():
    """Restore each aircraft's latest known fields from the CSV archive."""
    if not os.path.exists(config.HISTORY_PATH):
        return

    with _lock, open(config.HISTORY_PATH, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            hex_address = row.get("hex")
            if hex_address:
                _latest_by_hex[hex_address] = {
                    field: row.get(field, "") for field in config.HISTORY_FIELDS
                }


def append_message(message):
    """Merge one SBS message and append a timestamped aircraft record."""
    hex_address = message.get("hex")
    if not hex_address:
        return False

    with _lock:
        current = _latest_by_hex.setdefault(
            hex_address, {field: "" for field in config.HISTORY_FIELDS}
        )
        for field in config.HISTORY_FIELDS:
            value = message.get(field)
            if value is not None and value != "":
                current[field] = value

        row = {
            "time": f"{time.time():.3f}",
            "hex": hex_address,
            **current,
        }
        new_file = not os.path.exists(config.HISTORY_PATH) or os.path.getsize(
            config.HISTORY_PATH
        ) == 0
        with open(config.HISTORY_PATH, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            if new_file:
                writer.writeheader()
            writer.writerow(row)
    return True


def read_history_rows():
    """Return a copy of the CSV rows, excluding its header."""
    with _lock:
        try:
            with open(config.HISTORY_PATH, newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)
                return list(reader)
        except OSError:
            return []


def prune_history(now=None):
    """Delete archived records older than the configured retention period."""
    if config.HISTORY_RETENTION_DAYS <= 0:
        return 0

    now = time.time() if now is None else now
    cutoff = now - config.HISTORY_RETENTION_DAYS * 86400
    if not os.path.exists(config.HISTORY_PATH):
        return 0

    temp_path = config.HISTORY_PATH + ".tmp"
    removed = 0
    with _lock:
        with open(config.HISTORY_PATH, newline="", encoding="utf-8") as source, \
                open(temp_path, "w", newline="", encoding="utf-8") as target:
            reader = csv.DictReader(source)
            writer = csv.DictWriter(target, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for row in reader:
                try:
                    expired = float(row["time"]) < cutoff
                except (KeyError, ValueError, TypeError):
                    expired = False
                if expired:
                    removed += 1
                else:
                    writer.writerow(row)

        os.replace(temp_path, config.HISTORY_PATH)

        # Rebuild the in-memory latest records from the retained CSV.
        _latest_by_hex.clear()
        with open(config.HISTORY_PATH, newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                hex_address = row.get("hex")
                if hex_address:
                    _latest_by_hex[hex_address] = {
                        field: row.get(field, "")
                        for field in config.HISTORY_FIELDS
                    }
    return removed
