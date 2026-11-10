import time
import serial

import config

class Sender:
    def __init__(self):
        self.ser = serial.Serial(config.SERIAL_PORT, config.BAUD, timeout=1)

    def send_history(self, rows):
        """Send every history row, then END, and wait briefly for DONE."""
        self.ser.reset_input_buffer()
        sent = 0

        for row in rows:
            line = ",".join(row)
            self.ser.write((line + "\n").encode())
            sent += 1
            time.sleep(config.SEND_DELAY_S)

        self.ser.write(b"END\n")
        print(f"sent {sent} history rows")

        deadline = time.time() + config.REPLY_TIMEOUT_S
        while time.time() < deadline:
            reply = self.ser.readline().decode(errors="ignore").strip()
            if reply:
                print("received:", reply)
                if reply == "DONE":
                    break
