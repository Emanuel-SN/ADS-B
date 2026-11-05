import json
import config

def read_aircraft():
    """Return the list of aircraft dump1090 currently reports."""
    try:
        with open(config.JSON_PATH) as f:
            return json.load(f).get("aircraft", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []