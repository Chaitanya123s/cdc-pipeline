
import csv
from pathlib import Path

from src.cdc.validators import validate_event
from src.cdc.db import save_rejected_records


EXPECTED_FIELDS = {
    "event_id",
    "customer_id",
    "event_type",
    "event_timestamp",
    "customer_name",
    "run_id",
    "source_file",
    "source_seq",
}


def ingest_csv(file_path, run_id=None):
    """
    Read, validate and ingest customer CDC events.

    Invalid records are automatically saved in reject_events.

    Returns:
        valid_records: Validated event records.
        rejected_records: Rejected records with reasons.
    """

    valid_records = []
    rejected_records = []
    seen_event_ids = set()

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Input path is not a file: {file_path}"
        )

    try:
        with file_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file, strict=True)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV file is empty or has no header"
                )

            actual_fields = set(reader.fieldnames)

            if actual_fields != EXPECTED_FIELDS:
                raise ValueError(
                    f"Schema mismatch. "
                    f"Expected {sorted(EXPECTED_FIELDS)}, "
                    f"received {sorted(actual_fields)}"
                )

            if len(reader.fieldnames) != len(EXPECTED_FIELDS):
                raise ValueError(
                    "Duplicate column names found in CSV header"
                )

            for row_number, record in enumerate(reader, start=2):

                # Reject rows with extra columns
                if None in record:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": record,
                        "reason": "Unexpected extra CSV columns"
                    })
                    continue

                # Reject rows with missing values
                if any(value is None for value in record.values()):
                    rejected_records.append({
                        "row_number": row_number,
                        "record": record,
                        "reason": "Missing CSV column value"
                    })
                    continue

                event_id = record.get("event_id", "").strip()

                # Detect duplicate event IDs within this CSV
                if event_id and event_id in seen_event_ids:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": record,
                        "reason": f"Duplicate event ID in batch: {event_id}"
                    })
                    continue

                if event_id:
                    seen_event_ids.add(event_id)

                # Validate event
                is_valid, reason = validate_event(record)

                if is_valid:

                    record["event_type"] = (
                        record["event_type"].strip().upper()
                    )

                    record["source_seq"] = int(
                        record["source_seq"]
                    )
                    record["run_id"] = run_id or record.get("run_id")
                    record["source_file"] = Path(file_path).name
                    valid_records.append(record)

                else:
                    rejected_records.append({
                        "row_number": row_number,
                        "record": record,
                        "reason": reason
                    })

    except csv.Error as error:
        raise ValueError(
            f"Malformed CSV input: {error}"
        ) from error

    # Automatically persist rejected records
    if rejected_records:
        saved_count = save_rejected_records(
            rejected_records,
            default_source_file=file_path.name
        )

        print(
            f"Rejected records saved to database: {saved_count}"
        )

    return valid_records, rejected_records
