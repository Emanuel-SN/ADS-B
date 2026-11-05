import time, serial
import config

class Sender:
    def __init__(self):
        self.ser = serial.Serial(config.SERIAL_PORT, config.BAUD, timeout=1)

    @staticmethod
    def _fmt(v):
        return "" if v is None else str(v)

    def send(self, snapshot):
        """Send one line per plane, then END, then wait for DONE."""
        self.ser.reset_input_buffer()

        for h, t in snapshot.items():
            msg = ",".join([h] + [self._fmt(t.get(k)) for k in config.FIELDS])
            self.ser.write((msg + "\n").encode())
            print("sent:", msg)
            time.sleep(config.SEND_DELAY_S)
        self.ser.write(b"END\n")

        deadline = time.time() + config.REPLY_TIMEOUT_S
        while time.time() < deadline:
            reply = self.ser.readline().decode(errors="ignore").strip()
            if reply:
                print("received:", reply)
                if reply == "DONE":
                    break