
import csv
from pathlib import Path

from src.cdc.ingestion import ingest_csv


def test_empty_csv_returns_no_records(tmp_path):
    csv_file = tmp_path / "empty_events.csv"

    fields = [
        "event_id",
        "customer_id",
        "event_type",
        "event_timestamp",
        "customer_name",
        "run_id",
        "source_file",
        "source_seq",
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

    valid_records, rejected_records = ingest_csv(csv_file)

    assert valid_records == []
    assert rejected_records == []

import pytest


def test_csv_with_missing_column_is_rejected(tmp_path):
    csv_file = tmp_path / "missing_column.csv"

    csv_file.write_text(
        "event_id,customer_id,event_type,event_timestamp,customer_name,run_id,source_seq\n"
        "EVT_BAD,CUST_BAD,INSERT,2026-11-01T10:00:00Z,Test,RUN_TEST,1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        ingest_csv(csv_file)

def test_csv_with_extra_column_is_rejected(tmp_path):
    csv_file = tmp_path / "extra_column.csv"

    csv_file.write_text(
        "event_id,customer_id,event_type,event_timestamp,customer_name,run_id,source_file,source_seq\n"
        "EVT_BAD,CUST_BAD,INSERT,2026-11-01T10:00:00Z,Test,RUN_TEST,test.csv,1,UNEXPECTED\n",
        encoding="utf-8",
    )

    valid_records, rejected_records = ingest_csv(csv_file)

    assert len(valid_records) == 0
    assert len(rejected_records) == 1
