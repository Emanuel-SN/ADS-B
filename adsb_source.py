import socket
import time
import config


def parse_sbs_message(line):
    """Convert one SBS/BaseStation MSG line into the fields used by this app."""
    columns = line.strip().split(",")
    if len(columns) < 16 or columns[0] != "MSG":
        return None

    hex_address = columns[4].strip().lower()
    if not hex_address:
        return None

    def value(index):
        return columns[index].strip() or None

    return {
        "hex": hex_address,
        "flight": (value(10) or "").strip() or None,
        "alt": value(11),
        "gs": value(12),
        "track": value(13),
        "lat": value(14),
        "lon": value(15),
    }


def stream_sbs_lines():
    """Yield lines from dump1090, reconnecting if its TCP stream stops."""
    while True:
        try:
            print(f"connecting to dump1090 at {config.SBS_HOST}:{config.SBS_PORT}")
            with socket.create_connection(
                (config.SBS_HOST, config.SBS_PORT), timeout=5
            ) as connection:
                connection.settimeout(None)
                stream = connection.makefile("r", encoding="utf-8", newline="\n")
                with stream:
                    for line in stream:
                        yield line.rstrip("\r\n")
            time.sleep(config.SBS_RETRY_SECONDS)
        except OSError as error:
            print("dump1090 connection error:", error)
            time.sleep(config.SBS_RETRY_SECONDS)
