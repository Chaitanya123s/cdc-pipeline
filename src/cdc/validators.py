
from datetime import datetime, timezone


REQUIRED_FIELDS = [
    "event_id",
    "customer_id",
    "event_type",
    "event_timestamp",
    "customer_name",
    "run_id",
    "source_file",
]

VALID_EVENT_TYPES = {"INSERT", "UPDATE", "DELETE"}


def validate_event(event):
    """
    Validate an incoming customer CDC event.

    Returns:
        (True, None) if valid.
        (False, reason) if invalid.
    """

    if not isinstance(event, dict):
        return False, "Record must be a dictionary"

    # 1. Check required fields
    for field in REQUIRED_FIELDS:
        value = event.get(field)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            return False, f"Missing required field: {field}"

    # 2. Validate event type
    if not isinstance(event["event_type"], str):
        return False, "Event type must be a string"

    event_type = event["event_type"].strip().upper()

    if event_type not in VALID_EVENT_TYPES:
        return False, "Invalid event type"

    # 3. Validate timestamp
    if not isinstance(event["event_timestamp"], str):
        return False, "Timestamp must be a string"

    try:
        timestamp = datetime.fromisoformat(
            event["event_timestamp"].replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            return False, "Timestamp must include timezone information"

        timestamp.astimezone(timezone.utc)

    except (ValueError, TypeError):
        return False, "Invalid ISO-8601 timestamp"

    # 4. Validate source sequence
    source_seq = event.get("source_seq", 0)

    try:
        if isinstance(source_seq, bool):
            return False, "source_seq must be a non-negative integer"

        sequence_number = int(source_seq)

        if str(source_seq).strip() != str(sequence_number):
            return False, "source_seq must be an integer"

        if sequence_number < 0:
            return False, "source_seq cannot be negative"

    except (ValueError, TypeError):
        return False, "source_seq must be a non-negative integer"

    return True, None
