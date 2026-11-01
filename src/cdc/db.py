
import sqlite3
import json
import hashlib

from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).resolve().parents[2]
import os

DATABASE_PATH = Path(
    os.environ.get(
        "CDC_DATABASE_PATH",
        str(PROJECT_ROOT / "data" / "cdc_pipeline.db")
    )
)



def get_connection():
    """Create an optimized SQLite database connection."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    # Improve concurrent read/write handling
    connection.execute("PRAGMA journal_mode=WAL")

    # Reduce synchronization overhead while retaining
    # SQLite's normal durability guarantees
    connection.execute("PRAGMA synchronous=NORMAL")

    # Keep temporary tables and indexes in memory
    connection.execute("PRAGMA temp_store=MEMORY")

    return connection



def initialize_database():
    """Initialize database tables and apply missing column migrations."""

    with get_connection() as connection:

        # Customer current-state table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT,
                city TEXT,
                updated_at TEXT NOT NULL,
                run_id TEXT NOT NULL,
                source_file TEXT NOT NULL,
                is_deleted INTEGER NOT NULL DEFAULT 0,
                last_source_seq INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Customer event history
        connection.execute("""
            CREATE TABLE IF NOT EXISTS customer_events (
                event_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_timestamp TEXT NOT NULL,
                run_id TEXT NOT NULL,
                source_file TEXT NOT NULL,
                source_seq INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Rejected events
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reject_events (
                rejection_id TEXT PRIMARY KEY,
                row_number INTEGER,
                event_id TEXT,
                customer_id TEXT,
                record_json TEXT NOT NULL,
                rejection_reason TEXT NOT NULL,
                run_id TEXT,
                source_file TEXT,
                rejected_at TEXT NOT NULL
            )
        """)

        # Pipeline execution tracking
        connection.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                source_file TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                total_records INTEGER NOT NULL DEFAULT 0,
                processed_records INTEGER NOT NULL DEFAULT 0,
                rejected_records INTEGER NOT NULL DEFAULT 0,
                skipped_records INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                failure_reason TEXT
            )
        """)

        # Migrate existing databases safely
        migrations = {
            "customers": {
                "is_deleted": "INTEGER NOT NULL DEFAULT 0",
                "last_source_seq": "INTEGER NOT NULL DEFAULT 0"
            },
            "customer_events": {
                "source_seq": "INTEGER NOT NULL DEFAULT 0"
            }
        }

        for table, columns in migrations.items():

            existing_columns = {
                row["name"]
                for row in connection.execute(
                    f"PRAGMA table_info({table})"
                )
            }

            for column, definition in columns.items():

                if column not in existing_columns:
                    connection.execute(
                        f"ALTER TABLE {table} ADD COLUMN "
                        f"{column} {definition}"
                    )

    print("CDC database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")


def start_pipeline_run(run_id, source_file, total_records=0):
    """Record the beginning of a pipeline execution."""

    started_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO pipeline_runs (
                run_id,
                source_file,
                started_at,
                total_records,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            run_id,
            source_file,
            started_at,
            total_records,
            "RUNNING"
        ))

    print(f"Pipeline run started: {run_id}")


def finish_pipeline_run(
    run_id,
    status,
    total_records,
    processed_records,
    rejected_records,
    skipped_records,
    failure_reason=None
):
    """Record pipeline completion and execution metrics."""

    allowed_statuses = {"SUCCESS", "FAILED", "PARTIAL"}

    if status not in allowed_statuses:
        raise ValueError(f"Invalid pipeline status: {status}")

    counts = [
        total_records,
        processed_records,
        rejected_records,
        skipped_records
    ]

    if any(not isinstance(value, int) or value < 0 for value in counts):
        raise ValueError("Pipeline counts must be non-negative integers.")

    if processed_records + rejected_records + skipped_records > total_records:
        raise ValueError("Pipeline result counts exceed total records.")

    ended_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        cursor = connection.execute("""
            UPDATE pipeline_runs
            SET ended_at = ?,
                total_records = ?,
                processed_records = ?,
                rejected_records = ?,
                skipped_records = ?,
                status = ?,
                failure_reason = ?
            WHERE run_id = ?
              AND status = 'RUNNING'
        """, (
            ended_at,
            total_records,
            processed_records,
            rejected_records,
            skipped_records,
            status,
            failure_reason,
            run_id
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"Active pipeline run not found: {run_id}"
            )

    print(f"Pipeline run completed: {run_id} ({status})")


def save_rejected_records(
    rejected_records,
    default_run_id=None,
    default_source_file=None
):
    """Permanently save rejected CSV records."""

    saved_count = 0

    with get_connection() as connection:

        for rejected in rejected_records:

            record = rejected.get("record", {})
            reason = rejected.get(
                "reason",
                "Unknown rejection reason"
            )

            safe_record = {
    str(key): value
    for key, value in record.items()
}

            record_json = json.dumps(
                safe_record,
                sort_keys=True,
                default=str
            )

            row_number = rejected.get("row_number")
            event_id = record.get("event_id")
            customer_id = record.get("customer_id")
            run_id = record.get("run_id") or default_run_id
            source_file = (
                record.get("source_file") or default_source_file
            )

            # Deterministic rejection ID
            identity = (
                f"{source_file}|{run_id}|{row_number}|"
                f"{reason}|{record_json}"
            )

            rejection_id = hashlib.sha256(
                identity.encode("utf-8")
            ).hexdigest()

            cursor = connection.execute("""
                INSERT OR IGNORE INTO reject_events (
                    rejection_id,
                    row_number,
                    event_id,
                    customer_id,
                    record_json,
                    rejection_reason,
                    run_id,
                    source_file,
                    rejected_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rejection_id,
                row_number,
                event_id,
                customer_id,
                record_json,
                reason,
                run_id,
                source_file,
                datetime.now(timezone.utc).isoformat()
            ))

            saved_count += cursor.rowcount

    return saved_count


def get_event_order(timestamp, source_seq):
    """Create a comparable ordering key for CDC events."""

    event_time = datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    )

    if event_time.tzinfo is None:
        raise ValueError(
            "Event timestamp must include a timezone."
        )

    event_time = event_time.astimezone(timezone.utc)

    return event_time, int(source_seq)


def process_event(event):
    """
    Process CDC events with duplicate detection,
    event ordering and soft deletion.
    """

    event_type = event["event_type"].upper()
    source_seq = int(event.get("source_seq", 0))

    if source_seq < 0:
        raise ValueError("source_seq cannot be negative.")

    incoming_order = get_event_order(
        event["event_timestamp"],
        source_seq
    )

    with get_connection() as connection:

        # 1. Check duplicate events
        existing_event = connection.execute("""
            SELECT event_id
            FROM customer_events
            WHERE event_id = ?
        """, (event["event_id"],)).fetchone()

        if existing_event:
            print(
                f"Duplicate event skipped: {event['event_id']}"
            )
            return False

        # 2. Find existing customer
        customer = connection.execute("""
            SELECT *
            FROM customers
            WHERE customer_id = ?
        """, (event["customer_id"],)).fetchone()

        # 3. Check event ordering
        if customer:

            current_order = get_event_order(
                customer["updated_at"],
                customer["last_source_seq"]
            )

            if incoming_order <= current_order:

                # Store late event in history without applying it
                connection.execute("""
                    INSERT INTO customer_events (
                        event_id,
                        customer_id,
                        event_type,
                        event_timestamp,
                        run_id,
                        source_file,
                        source_seq
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event["event_id"],
                    event["customer_id"],
                    event_type,
                    event["event_timestamp"],
                    event["run_id"],
                    event["source_file"],
                    source_seq
                ))

                print(
                    f"Late event recorded but not applied: "
                    f"{event['event_id']}"
                )

                return False

        # 4. Apply INSERT
        if event_type == "INSERT":

            if customer is None:

                connection.execute("""
                    INSERT INTO customers (
                        customer_id,
                        customer_name,
                        updated_at,
                        run_id,
                        source_file,
                        is_deleted,
                        last_source_seq
                    )
                    VALUES (?, ?, ?, ?, ?, 0, ?)
                """, (
                    event["customer_id"],
                    event["customer_name"],
                    event["event_timestamp"],
                    event["run_id"],
                    event["source_file"],
                    source_seq
                ))

            else:

                # Reactivate customer if this INSERT is newer
                connection.execute("""
                    UPDATE customers
                    SET customer_name = ?,
                        updated_at = ?,
                        run_id = ?,
                        source_file = ?,
                        is_deleted = 0,
                        last_source_seq = ?
                    WHERE customer_id = ?
                """, (
                    event["customer_name"],
                    event["event_timestamp"],
                    event["run_id"],
                    event["source_file"],
                    source_seq,
                    event["customer_id"]
                ))

        # 5. Apply UPDATE
        elif event_type == "UPDATE":

            if customer is None or customer["is_deleted"] == 1:
                raise ValueError(
                    f"Active customer not found: "
                    f"{event['customer_id']}"
                )

            connection.execute("""
                UPDATE customers
                SET customer_name = ?,
                    updated_at = ?,
                    run_id = ?,
                    source_file = ?,
                    last_source_seq = ?
                WHERE customer_id = ?
                  AND is_deleted = 0
            """, (
                event["customer_name"],
                event["event_timestamp"],
                event["run_id"],
                event["source_file"],
                source_seq,
                event["customer_id"]
            ))

        # 6. Apply soft DELETE
        elif event_type == "DELETE":

            if customer is None or customer["is_deleted"] == 1:
                raise ValueError(
                    f"Active customer not found: "
                    f"{event['customer_id']}"
                )

            connection.execute("""
                UPDATE customers
                SET is_deleted = 1,
                    updated_at = ?,
                    run_id = ?,
                    source_file = ?,
                    last_source_seq = ?
                WHERE customer_id = ?
            """, (
                event["event_timestamp"],
                event["run_id"],
                event["source_file"],
                source_seq,
                event["customer_id"]
            ))

        else:
            raise ValueError(
                f"Unsupported event type: {event_type}"
            )

        # 7. Record successfully processed event
        connection.execute("""
            INSERT INTO customer_events (
                event_id,
                customer_id,
                event_type,
                event_timestamp,
                run_id,
                source_file,
                source_seq
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event["event_id"],
            event["customer_id"],
            event_type,
            event["event_timestamp"],
            event["run_id"],
            event["source_file"],
            source_seq
        ))

    return True


if __name__ == "__main__":
    initialize_database()
