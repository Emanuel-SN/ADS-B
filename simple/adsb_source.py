"""Read antirez/dump1090's local SBS/BaseStation TCP stream."""

import socket
import time

import config


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
