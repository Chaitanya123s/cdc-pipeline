
# Data Dictionary

## 1. Overview

This document defines the tables, columns, data types, keys, and business meaning used in the Customer CDC Pipeline.

All table and column names follow snake_case naming conventions.

## 2. dim_region

Stores valid customer region reference values.

| Column | Data Type | Constraint | Description |
|---|---|---|---|
| region_code | TEXT | PRIMARY KEY | Unique region identifier |
| region_name | TEXT | NOT NULL | Region name |

## 3. customer_event_history

Stores every accepted unique customer event.

| Column | Data Type | Constraint | Description |
|---|---|---|---|
| event_id | TEXT | PRIMARY KEY | Unique event identifier |
| customer_id | TEXT | NOT NULL | Customer business key |
| op_type | TEXT | NOT NULL | I, U, or D |
| event_ts | TEXT | NOT NULL | Event timestamp in UTC |
| source_seq | INTEGER | NOT NULL | Event ordering sequence |
| email | TEXT | NULL | Customer email |
| full_name | TEXT | NULL | Customer full name |
| region_code | TEXT | NULL | Customer region |
| status | TEXT | NULL | Customer status |
| source_file | TEXT | NOT NULL | Input file name |
| run_id | TEXT | NOT NULL | Processing run identifier |
| is_late | INTEGER | NOT NULL | Indicates a late-arriving event |

## 4. customer_current

Stores the latest state of each customer.

| Column | Data Type | Constraint | Description |
|---|---|---|---|
| customer_id | TEXT | PRIMARY KEY | Unique customer identifier |
| email | TEXT | NULL | Latest customer email |
| full_name | TEXT | NULL | Latest customer name |
| region_code | TEXT | NULL | Latest region code |
| status | TEXT | NULL | Latest customer status |
| is_deleted | INTEGER | NOT NULL | Soft-delete indicator |
| deleted_at | TEXT | NULL | Delete timestamp |
| last_event_id | TEXT | NOT NULL | Latest event identifier |
| last_event_ts | TEXT | NOT NULL | Latest event timestamp |
| updated_run_id | TEXT | NOT NULL | Last processing run |

## 5. reject_events

Stores invalid or malformed input records.

| Column | Data Type | Constraint | Description |
|---|---|---|---|
| reject_id | INTEGER | PRIMARY KEY | Unique rejection identifier |
| raw_record | TEXT | NULL | Original input record |
| reject_reason | TEXT | NOT NULL | Reason for rejection |
| source_file | TEXT | NOT NULL | Input file name |
| line_no | INTEGER | NOT NULL | Input line number |
| run_id | TEXT | NOT NULL | Processing run identifier |

## 6. pipeline_runs

Tracks pipeline execution and operational metrics.

| Column | Data Type | Constraint | Description |
|---|---|---|---|
| run_id | TEXT | PRIMARY KEY | Unique execution identifier |
| started_at | TEXT | NOT NULL | Run start time in ISO-8601 UTC |
| ended_at | TEXT | NULL | Run completion time |
| status | TEXT | NOT NULL | SUCCESS or FAILED |
| input_count | INTEGER | NOT NULL | Total input records |
| accepted_count | INTEGER | NOT NULL | Newly accepted events |
| duplicate_count | INTEGER | NOT NULL | Duplicate events |
| rejected_count | INTEGER | NOT NULL | Rejected records |
| late_count | INTEGER | NOT NULL | Late-arriving events |
| failure_reason | TEXT | NULL | Failure description |

## 7. Key Relationships

- customer_event_history.event_id is the event primary key.
- customer_current.customer_id identifies one customer.
- dim_region.region_code validates customer region references.
- pipeline_runs.run_id identifies each pipeline execution.
- run_id and source_file provide processing lineage.

## 8. Data Type Conventions

- TEXT: String values and ISO-8601 timestamps.
- INTEGER: Counts, sequences, and Boolean-like flags.
- UTC: Standard timezone for event timestamps.
- snake_case: Naming convention for tables and columns.
