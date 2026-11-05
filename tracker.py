import time, threading
import config

class Tracker:
    """Keeps one growing record per plane, never overwriting data with blanks."""

    def __init__(self, tracks=None):
        self.tracks = tracks or {}
        self.lock = threading.Lock()

    def update(self, aircraft):
        """Merge new data. Returns rows for every plane whose data changed."""
        now = time.time()
        rows = []
        with self.lock:
            for a in aircraft:
                h = a.get("hex")
                if not h or a.get("seen", 99) > config.STALE_S:
                    continue
                incoming = {
                    "flight": (a.get("flight") or "").strip() or None,
                    "alt": a.get("alt_baro"),
                    "gs": a.get("gs"),
                    "track": a.get("track"),
                    "lat": a.get("lat"),
                    "lon": a.get("lon"),
                }
                t = self.tracks.setdefault(h, {"first_seen": now})
                changed = False
                for k, v in incoming.items():
                    if v is not None and t.get(k) != v:
                        t[k] = v
                        changed = True
                t["last_seen"] = now
                if changed:
                    rows.append([round(now, 1), h] + [t.get(k, "") for k in config.FIELDS])

            for h in [h for h, t in self.tracks.items()
                      if now - t["last_seen"] > config.EXPIRE_S]:
                del self.tracks[h]
        return rows

    def snapshot(self):
        """Copy of planes recent enough to send."""
        now = time.time()
        with self.lock:
            return {h: dict(t) for h, t in self.tracks.items()
                    if now - t["last_seen"] <= config.SEND_MAX_AGE}

    def export(self):
        with self.lock:
            return {h: dict(t) for h, t in self.tracks.items()}