"""Send the text history when the GPIO input is triggered."""

import time

import serial

import config
import storage


def send_history():
    rows = storage.read_history()
    sent = 0

    try:
        with serial.Serial(config.SERIAL_PORT, config.SERIAL_BAUD, timeout=1) as port:
            port.reset_input_buffer()
            for row in rows:
                values = [row.get(name, "") or "" for name in ("time", "hex", "flight", "alt", "gs", "track", "lat", "lon")]
                line = "|".join(values) + "\n"
                port.write(line.encode())
                sent += 1
                time.sleep(0.02)

            port.write(("END" + "\n").encode())
            print(f"Sent {sent} rows")

            deadline = time.time() + 3
            while time.time() < deadline:
                reply = port.readline().decode(errors="ignore").strip()
                if reply:
                    print("Received:", reply)
                    if reply == "DONE":
                        break
    except serial.SerialException as error:
        print("Could not open serial port:", error)
