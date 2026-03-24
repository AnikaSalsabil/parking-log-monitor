#!/bin/bash

# ─────────────────────────────────────────────────────────────
# monitor.sh
# Watches parking_events.log in real time.
# When it sees an ERROR or WARN line, it prints a loud alert
# and saves it to alerts.log.
#
# This uses core Linux tools:
#   tail -f  = watch a file live as new lines are added
#   grep     = search for a pattern inside text
#   awk      = extract specific columns from text
# ─────────────────────────────────────────────────────────────

LOG_FILE="parking_events.log"
ALERT_FILE="alerts.log"

# ── Startup banner ──────────────────────────────────────────
echo "======================================================"
echo "  Parking Log Monitor"
echo "  Started: $(date)"
echo "  Watching: $LOG_FILE"
echo "======================================================"
echo ""

# Check the log file exists before we try to watch it
# -f means "is this a regular file?"
if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: $LOG_FILE not found."
    echo "Please run simulate_logs.py first, then restart this script."
    exit 1
fi

# ── Main monitoring loop ─────────────────────────────────────
# tail -f keeps watching the file and outputs new lines as they arrive
# The pipe | sends each new line into our while loop one at a time
tail -f "$LOG_FILE" | while IFS= read -r line; do

    # Print every line so we can see all activity
    echo "[MONITOR] $line"

    # ── Check for ERROR ──────────────────────────────────────
    # grep -q means "search quietly" - returns true/false without printing
    if echo "$line" | grep -q "ERROR"; then

        # Extract the camera name using awk
        # awk -F= splits on "=" character, $2 is the part after "camera="
        camera=$(echo "$line" | awk -F'camera=' '{print $2}' | awk '{print $1}')

        echo ""
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "  ALERT: ERROR DETECTED"
        echo "  Time   : $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  Camera : $camera"
        echo "  Line   : $line"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo ""

        # Save this alert to alerts.log with a timestamp
        echo "$(date '+%Y-%m-%d %H:%M:%S') | ERROR | $line" >> "$ALERT_FILE"
    fi

    # ── Check for WARN ───────────────────────────────────────
    if echo "$line" | grep -q "WARN"; then

        # Extract the plate number
        plate=$(echo "$line" | awk -F'plate=' '{print $2}' | awk '{print $1}')

        echo ""
        echo "----------------------------------------------"
        echo "  WARNING DETECTED"
        echo "  Time  : $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  Plate : $plate"
        echo "  Line  : $line"
        echo "----------------------------------------------"
        echo ""

        echo "$(date '+%Y-%m-%d %H:%M:%S') | WARN  | $line" >> "$ALERT_FILE"
    fi

done

