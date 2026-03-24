import psycopg2

# ─────────────────────────────────────────────────────────────
# query_report.py
# Connects to PostgreSQL and runs analysis queries to show
# system health - exactly what a QA engineer would check
# after a deployment or at end of day.
# ─────────────────────────────────────────────────────────────

DB_CONFIG = {
    "dbname":   "parking_db",
    "user":     "parkinguser",
    "password": "parking123",
    "host":     "localhost",
    "port":     "5432"
}


def run_query(conn, title, sql):
    """Run a query and print results in a readable format."""
    print(f"\n{'='*54}")
    print(f"  {title}")
    print(f"{'='*54}")
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        if not rows:
            print("  No data yet.")
            return
        # Print column headers
        col_names = [desc[0] for desc in cur.description]
        print("  " + " | ".join(f"{c:<15}" for c in col_names))
        print("  " + "-" * 50)
        # Print each row
        for row in rows:
            print("  " + " | ".join(f"{str(v):<15}" for v in row))


def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Could not connect: {e}")
        return

    print("\nParking System - QA Database Report")
    print(f"{'='*54}")

    # Total event count
    run_query(conn,
        "Event count by type",
        """
        SELECT event_type, COUNT(*) AS total
        FROM parking_events
        GROUP BY event_type
        ORDER BY total DESC
        """
    )

    # All payment failures
    run_query(conn,
        "Payment failures",
        """
        SELECT event_time, plate, notes
        FROM parking_events
        WHERE status = 'FAILED'
        ORDER BY event_time DESC
        LIMIT 10
        """
    )

    # Camera errors - which camera failed most
    run_query(conn,
        "Camera errors by camera",
        """
        SELECT camera, COUNT(*) AS error_count
        FROM parking_events
        WHERE notes LIKE 'ERROR%'
        AND camera IS NOT NULL
        GROUP BY camera
        ORDER BY error_count DESC
        """
    )

    # Vehicles with no exit (still parked)
    run_query(conn,
        "Vehicles entered but not yet exited",
        """
        SELECT plate, MAX(event_time) AS entry_time
        FROM parking_events
        WHERE event_type = 'ENTRY'
        AND plate NOT IN (
            SELECT plate FROM parking_events
            WHERE event_type = 'EXIT'
            AND plate IS NOT NULL
        )
        GROUP BY plate
        ORDER BY entry_time DESC
        LIMIT 10
        """
    )

    # Recent errors
    run_query(conn,
        "Last 5 errors",
        """
        SELECT event_time, event_type, camera, notes
        FROM parking_events
        WHERE notes LIKE 'ERROR%'
        ORDER BY event_time DESC
        LIMIT 5
        """
    )

    conn.close()
    print(f"\n{'='*54}\n")


if __name__ == "__main__":
    main()

