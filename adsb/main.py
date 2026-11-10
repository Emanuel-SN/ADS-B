
import queue
import threading
import time

from gpiozero import DigitalInputDevice

import config
import storage
from sender import send_history
from source import save_messages


def read_terminal_commands(commands):
    while True:
        try:
            command = input("Command (send!): ").strip().lower()
        except EOFError:
            return

        if command == "send!":
            commands.put("send!")
        elif command:
            print("Unknown command. Type send! to transmit the history.")


def main():
    config.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    storage.remove_old_rows()
    storage.load_previous_values()
    threading.Thread(target=save_messages, daemon=True).start()
    commands = queue.Queue()
    threading.Thread(target=read_terminal_commands, args=(commands,), daemon=True).start()

    request = DigitalInputDevice(config.GPIO_PIN, pull_up=False)
    was_high = False
    last_cleanup = time.time()

    try:
        while True:
            now = time.time()
            if now - last_cleanup >= 300:
                storage.remove_old_rows(now)
                last_cleanup = now

            try:
                command = commands.get_nowait()
            except queue.Empty:
                command = None
            if command == "send!":
                send_history()

            is_high = bool(request.value)
            if is_high and not was_high:
                send_history()
            was_high = is_high
            time.sleep(0.02)
    finally:
        request.close()


if __name__ == "__main__":
    main()
