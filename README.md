
# Customer Change Data Capture (CDC) Pipeline

## 1. Project Overview

This project implements a local Change Data Capture (CDC) pipeline using Python and SQLite.

The pipeline processes customer data events representing Insert (I), Update (U), and Delete (D) operations.

It validates incoming events, handles duplicate and out-of-order records, maintains an event history, and updates the current customer state.

## 2. Project Objectives

- Process customer insert, update, and delete events.
- Validate incoming records against defined schemas and business rules.
- Handle duplicate and late-arriving events.
- Maintain historical event records.
- Maintain the latest customer state.
- Quarantine invalid records with rejection reasons.
- Support safe reruns and reproducible processing.
- Generate operational and reconciliation reports.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| SQLite | Local database |
| SQL | Data storage and reconciliation |
| Pytest | Automated testing |
| Git | Version control |

## 4. High-Level Architecture

Input Events
    |
    v
Data Reader
    |
    v
Schema and Business Validation
    |
    +---- Invalid Records ----> Reject / Quarantine
    |
    v
Duplicate Detection
    |
    v
Event History Table
    |
    v
Current Customer State
    |
    v
Reconciliation and Reports

## 5. Project Structure

```text
cdc-pipeline/
├── README.md
├── requirements.txt
├── docs/
├── src/
│   └── cdc/
├── scripts/
├── data/
│   ├── sample/
│   └── expected/
├── tests/
└── reports/
```

## 6. Processing Assumptions

- Incoming events contain full customer record images.
- Events use ISO-8601 timestamps normalized to UTC.
- Event ordering is based on event timestamp and source sequence.
- Deletes are implemented as soft deletes.
- Historical event records are retained.
- Older events cannot overwrite newer customer state.
- Newer insert events can reactivate previously deleted customers.

## 7. Data Quality

The pipeline will handle:

- Missing required fields.
- Invalid timestamps.
- Invalid operation types.
- Duplicate event identifiers.
- Unknown region reference keys.
- Malformed input records.
- Unexpected schema changes.
- Empty input batches.
## 8. Setup and Execution

### Prerequisites
- Python 3.10 or later
- pip

### Installation

Create a virtual environment:

    python -m venv venv

Activate on Windows PowerShell:

    .\venv\Scripts\Activate.ps1

Install dependencies:

    pip install -r requirements.txt

### Run the sample pipeline

    python -m src.cdc.pipeline

### Generate synthetic benchmark data

    python scripts/generate_large_dataset.py

### Run benchmark

    python scripts/benchmark_pipeline.py

### Run automated tests

    python -m pytest -v

## 9. Testing and Validation

The project includes automated tests covering:

- Valid event processing
- Missing required customer identifiers
- Invalid event types
- Malformed timestamps
- Timestamps without timezone information
- Negative source sequence values
- Duplicate event handling
- Late-arriving event handling
- Empty CSV input
- Missing CSV columns
- Extra CSV columns

Run tests using:

    python -m pytest -v

Latest verified result: 11 tests passed.

### Large Dataset Benchmark

The pipeline successfully processed a synthetic dataset of 100,000 customer events.

- Total events: 100,000
- Processed events: 100,000
- Rejected events: 0
- Skipped events: 0
- Execution time: 592.947 seconds
- Throughput: 168.65 events/second
- Pipeline status: SUCCESS
- Reconciliation: PASSED

## 10. Limitations and Future Improvements

- SQLite is intended for a local demonstration.
- Large-scale distributed processing is outside the initial scope.
- Future versions could use Apache Spark, Delta Lake, or a streaming platform.

## 11. Naming Conventions

- Database tables and columns use snake_case.
- Timestamps use ISO-8601 format in UTC.
- Every processing run has a unique run_id.
- Source records retain source_file information.
- Primary keys and foreign keys are explicitly defined.
