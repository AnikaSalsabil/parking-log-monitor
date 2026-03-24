import psycopg2
import time
import re
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# db_logger.py
# Watches parking_events.log in real time (like tail -f but
# in Python), parses each line into structured fields, and
# inserts a clean record into PostgreSQL.
#
# This is what a QA engineer does to track system behaviour
# over time - turning raw log text into queryable data.
# ─────────────────────────────────────────────────────────────

LOG_FILE = "parking_events.log"

# These are the connection details for our PostgreSQL database
# Must match exactly what we set up in Step 1
DB_CONFIG = {
    "dbname":   "parking_db",
    "user":     "parkinguser",
    "password": "parking123",
    "host":     "localhost",
    "port":     "5432"
}


def connect_db():
    """Connect to PostgreSQL and return the connection object."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected to PostgreSQL successfully.")
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Make sure PostgreSQL is running: sudo service postgresql start")
        exit(1)


def parse_log_line(line):
    """
    Takes one raw log line and extracts structured fields.
    Returns a dictionary of fields, or None if unparseable.

    Example input:
    "2026-03-24 10:23:01 INFO  ENTRY   plate=ABC123 camera=CAM_01"

    Example output:
    {
        "event_time": datetime(2026, 3, 24, 10, 23, 1),
        "event_type": "ENTRY",
        "plate":      "ABC123",
        "camera":     "CAM_01",
        "status":     None,
        "notes":      "Normal event"
    }
    """
    line = line.strip()

    # Skip empty lines
    if not line:
        return None

    # Extract timestamp - always the first 19 characters
    try:
        event_time = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Line doesn't start with a timestamp - skip it
        return None

    # Identify event type by scanning for known keywords
    event_type = None
    for keyword in ["ENTRY", "EXIT", "PAYMENT", "CAMERA", "SYSTEM"]:
        if keyword in line:
            event_type = keyword
            break

    if not event_type:
        return None

    # re.search looks for a pattern anywhere in the string
    # r'plate=(\S+)' means: find "plate=" then capture non-space characters
    plate_match  = re.search(r'plate=(\S+)',  line)
    camera_match = re.search(r'camera=(\S+)', line)
    status_match = re.search(r'status=(\S+)', line)

    # .group(1) returns the captured part (what was inside the brackets)
    plate  = plate_match.group(1)  if plate_match  else None
    camera = camera_match.group(1) if camera_match else None
    status = status_match.group(1) if status_match else None

    # Classify severity based on log level in the line
    if "ERROR" in line:
        notes = "ERROR - requires investigation"
    elif "WARN" in line:
        notes = "Warning - monitor closely"
    else:
        notes = "Normal event"

    return {
        "event_time": event_time,
        "event_type": event_type,
        "plate":      plate,
        "camera":     camera,
        "status":     status,
        "notes":      notes
    }


def insert_event(conn, event):
    """
    Inserts one parsed event into the parking_events table.
    Uses parameterised query (%(key)s) which is safe against
    SQL injection - important in any production system.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO parking_events
                (event_time, event_type, plate, camera, status, notes)
            VALUES
                (%(event_time)s, %(event_type)s, %(plate)s,
                 %(camera)s,     %(status)s,     %(notes)s)
        """, event)
    # commit() saves the insert permanently to the database
    conn.commit()


def follow_log(filepath):
    """
    Generator function that yields new lines from a file
    as they are written - the Python equivalent of tail -f.

    seek(0, 2) jumps to the end of the file so we only
    process new lines, not lines that already existed.
    """
    with open(filepath, "r") as f:
        # Jump to end of file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                # New line arrived - yield it to the caller
                yield line
            else:
                # No new line yet - wait half a second and try again
                time.sleep(0.5)


def main():
    # Wait for the log file to exist before starting
    import os
    if not os.path.exists(LOG_FILE):
        print(f"Waiting for {LOG_FILE} to be created...")
        print("Start simulate_logs.py in another terminal first.")
        while not os.path.exists(LOG_FILE):
            time.sleep(1)

    print(f"Watching {LOG_FILE} and inserting into PostgreSQL...\n")

    conn = connect_db()

    # Process each new line as it arrives
    for line in follow_log(LOG_FILE):
        event = parse_log_line(line)
        if event:
            insert_event(conn, event)
            # Print confirmation so we can see it working
            print(
                f"Inserted | {event['event_type']:<8} | "
                f"plate={str(event['plate']):<8} | "
                f"camera={str(event['camera']):<7} | "
                f"{event['notes']}"
            )


if __name__ == "__main__":
    main()

