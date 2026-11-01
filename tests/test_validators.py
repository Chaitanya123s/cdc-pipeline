
import pytest

from src.cdc.validators import validate_event


@pytest.fixture
def valid_event():
    return {
        "event_id": "TEST_VALID_001",
        "customer_id": "CUST_VALID_001",
        "event_type": "INSERT",
        "event_timestamp": "2026-11-01T10:00:00Z",
        "customer_name": "Test Customer",
        "run_id": "RUN_TEST",
        "source_file": "test.csv",
        "source_seq": "1",
    }


def test_valid_event(valid_event):
    is_valid, reason = validate_event(valid_event)

    assert is_valid is True
    assert reason is None


def test_missing_customer_id(valid_event):
    valid_event.pop("customer_id")

    is_valid, reason = validate_event(valid_event)

    assert is_valid is False
    assert "Missing required field" in reason


def test_invalid_event_type(valid_event):
    valid_event["event_type"] = "INVALID"

    is_valid, reason = validate_event(valid_event)

    assert is_valid is False
    assert reason == "Invalid event type"


def test_malformed_timestamp(valid_event):
    valid_event["event_timestamp"] = "not-a-timestamp"

    is_valid, reason = validate_event(valid_event)

    assert is_valid is False
    assert reason == "Invalid ISO-8601 timestamp"


def test_timestamp_without_timezone(valid_event):
    valid_event["event_timestamp"] = "2026-11-01T10:00:00"

    is_valid, reason = validate_event(valid_event)

    assert is_valid is False
    assert reason == "Timestamp must include timezone information"


def test_negative_source_sequence(valid_event):
    valid_event["source_seq"] = "-1"

    is_valid, reason = validate_event(valid_event)

    assert is_valid is False
    assert "source_seq" in reason
