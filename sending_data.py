import serial, time, json
from gpiozero import DigitalInputDevice

enable = 23
JSON_PATH = "/tmp/adsb/aircraft.json"

ser = serial.Serial("/dev/serial0", 115200, timeout=1)
request = DigitalInputDevice(enable, pull_up=False)

def get_aircraft():
    try:
        with open(JSON_PATH) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return data.get("aircraft", [])

def fmt(v):
    return "" if v is None else str(v)

def send_data():
    ser.reset_input_buffer()

    for a in get_aircraft():
        msg = ",".join([
            fmt(a.get("hex")),
            fmt((a.get("flight") or "").strip()),
            fmt(a.get("alt_baro")),
            fmt(a.get("gs")),
            fmt(a.get("track")),
            fmt(a.get("lat")),
            fmt(a.get("lon")),
        ])
        ser.write((msg + "\n").encode())
        print("sent:", msg)
        time.sleep(0.05)

    ser.write(b"END\n")

    deadline = time.time() + 3
    while time.time() < deadline:
        reply = ser.readline().decode(errors="ignore").strip()
        if reply:
            print("received:", reply)
            if reply == "DONE":
                break

was_high = False
while True:
    if request.value and not was_high:
        send_data()
    was_high = bool(request.value)
    time.sleep(0.02)