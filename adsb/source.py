import socket
import config
import time
import storage


def parse_message(line):
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
    while True:
        try:
            with socket.create_connection((config.SBS_HOST, config.SBS_PORT), 5) as sock:
                with sock.makefile("r", encoding="utf-8") as stream:
                    for line in stream:
                        message = parse_message(line)
                        if message:
                            yield message
        except OSError:
            pass
        time.sleep(2)


def save_messages():
    for message in messages():
        try:
            storage.save_message(message)
        except Exception as error:
            print("Could not save aircraft message:", error)
