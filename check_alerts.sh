#!/bin/bash

# ─────────────────────────────────────────────────────────────
# check_alerts.sh
# A quick summary tool - shows you what went wrong today.
# Uses grep, sort, and uniq to analyse the alerts log.
# ─────────────────────────────────────────────────────────────

ALERT_FILE="alerts.log"

if [ ! -f "$ALERT_FILE" ]; then
    echo "No alerts log found yet. Run the monitor first."
    exit 1
fi

echo "======================================================"
echo "  Alert Summary Report"
echo "  Generated: $(date)"
echo "======================================================"
echo ""

# Count total alerts
total=$(wc -l < "$ALERT_FILE")
echo "Total alerts logged: $total"
echo ""

# Count ERROR alerts
# grep -c counts how many lines match
errors=$(grep -c "ERROR" "$ALERT_FILE")
echo "Errors  : $errors"

# Count WARN alerts
warnings=$(grep -c "WARN" "$ALERT_FILE")
echo "Warnings: $warnings"

echo ""
echo "── Last 5 alerts ─────────────────────────────────────"
# tail -5 shows the last 5 lines of the file
tail -5 "$ALERT_FILE"

echo ""
echo "── Camera errors ──────────────────────────────────────"
# grep filters only ERROR lines, then we extract camera names
grep "ERROR" "$ALERT_FILE" | \
    awk -F'camera=' '{print $2}' | \
    awk '{print $1}' | \
    sort | \
    uniq -c | \
    sort -rn
# sort    = alphabetically sort the camera names
# uniq -c = count duplicates (how many times each camera appeared)
# sort -rn = sort by count, highest first

echo ""
echo "── Payment failures ───────────────────────────────────"
grep "WARN" "$ALERT_FILE" | \
    awk -F'plate=' '{print $2}' | \
    awk '{print $1}' | \
    sort | \
    uniq -c | \
    sort -rn

