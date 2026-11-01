
import uuid

from src.cdc.db import initialize_database, process_event, get_connection


def test_duplicate_event_is_not_processed():
    initialize_database()

    unique_id = uuid.uuid4().hex[:12].upper()

    event = {
        "event_id": f"AUTO_DUP_{unique_id}",
        "customer_id": f"AUTO_CUST_{unique_id}",
        "event_type": "INSERT",
        "event_timestamp": "2026-11-01T10:00:00+00:00",
        "customer_name": "Duplicate Test",
        "run_id": "RUN_AUTO_TEST",
        "source_file": "test_db.py",
        "source_seq": 1,
    }

    first_result = process_event(event)
    second_result = process_event(event)

    assert first_result is True
    assert second_result is False

    connection = get_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM customer_events WHERE event_id = ?",
        (event["event_id"],)
    ).fetchone()[0]

    connection.close()

    assert count == 1

def test_late_event_does_not_overwrite_newer_data():
    initialize_database()

    unique_id = uuid.uuid4().hex[:12].upper()
    customer_id = f"LATE_CUST_{unique_id}"

    newer_event = {
        "event_id": f"NEWER_{unique_id}",
        "customer_id": customer_id,
        "event_type": "INSERT",
        "event_timestamp": "2026-11-01T15:00:00+00:00",
        "customer_name": "New Customer Name",
        "run_id": "RUN_LATE_TEST",
        "source_file": "test_db.py",
        "source_seq": 100,
    }

    older_event = {
        "event_id": f"OLDER_{unique_id}",
        "customer_id": customer_id,
        "event_type": "UPDATE",
        "event_timestamp": "2026-11-01T14:00:00+00:00",
        "customer_name": "Old Customer Name",
        "run_id": "RUN_LATE_TEST",
        "source_file": "test_db.py",
        "source_seq": 90,
    }

    assert process_event(newer_event) is True
    assert process_event(older_event) is False

    connection = get_connection()

    customer = connection.execute(
        "SELECT customer_name, last_source_seq FROM customers WHERE customer_id = ?",
        (customer_id,)
    ).fetchone()

    connection.close()

    assert customer["customer_name"] == "New Customer Name"
    assert customer["last_source_seq"] == 100
