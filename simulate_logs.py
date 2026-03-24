import random
import time
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# simulate_logs.py
# Pretends to be a parking system by writing fake events
# to a log file every 2 seconds.
# Real parking systems write logs exactly like this.
# ─────────────────────────────────────────────────────────────

# Fake number plates our simulator will use
PLATES = ["ABC123", "XYZ999", "DEF456", "GHJ789", "KLM321", "NOP654"]

# Fake camera names (like the cameras at a car park entrance/exit)
CAMERAS = ["CAM_01", "CAM_02", "CAM_03"]

# This is the file we write log lines into
LOG_FILE = "parking_events.log"


def timestamp():
    # Returns current time as a string, e.g. "2026-03-24 10:23:01"
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log(line):
    # Writes one line to the log file AND prints it on screen
    # "a" means append - adds to end of file without deleting old lines
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def simulate():
    print("Parking log simulator started. Press Ctrl+C to stop.\n")

    while True:
        # Pick a random event type
        # weights = how often each event happens (out of 100)
        event = random.choices(
            ["ENTRY", "EXIT", "PAYMENT_OK", "PAYMENT_FAIL", "CAMERA_ERROR", "SYSTEM"],
            weights=[25, 25, 20, 10, 10, 10]
        )[0]

        plate  = random.choice(PLATES)
        camera = random.choice(CAMERAS)

        if event == "ENTRY":
            # A car drives in and the camera reads its plate
            write_log(
                f"{timestamp()} INFO  ENTRY   "
                f"plate={plate} camera={camera}"
            )

        elif event == "EXIT":
            # A car drives out - log how long it was parked
            duration = random.randint(5, 180)
            write_log(
                f"{timestamp()} INFO  EXIT    "
                f"plate={plate} camera={camera} duration={duration}min"
            )

        elif event == "PAYMENT_OK":
            # Car paid successfully
            amount = round(random.uniform(5.0, 40.0), 2)
            write_log(
                f"{timestamp()} INFO  PAYMENT "
                f"plate={plate} status=SUCCESS amount=${amount}"
            )

        elif event == "PAYMENT_FAIL":
            # Payment failed - this is a WARN level event
            write_log(
                f"{timestamp()} WARN  PAYMENT "
                f"plate={plate} status=FAILED reason=card_declined"
            )

        elif event == "CAMERA_ERROR":
            # Camera stopped responding - this is an ERROR level event
            write_log(
                f"{timestamp()} ERROR CAMERA  "
                f"camera={camera} msg=frame_timeout"
            )

        elif event == "SYSTEM":
            # System is alive and healthy - routine heartbeat
            write_log(
                f"{timestamp()} INFO  SYSTEM  "
                f"msg=heartbeat status=ok"
            )

        # Wait 2 seconds before writing the next event
        time.sleep(2)


# This line means: only run simulate() if we run THIS file directly
# (not if another file imports it)
if __name__ == "__main__":
    simulate()

