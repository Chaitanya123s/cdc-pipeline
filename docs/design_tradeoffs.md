
# Design Decisions and Trade-offs

## 1. Project Architecture

The CDC pipeline uses a modular Python architecture with SQLite as the local database.

The pipeline separates data reading, validation, event processing, storage, logging, and reconciliation into independent modules.

This improves maintainability, testability, and debugging.

## 2. Technology Selection

### Python
Python is used because it provides simple file handling, database connectivity, data processing, and testing capabilities.

### SQLite
SQLite is selected because it is lightweight, locally runnable, and does not require a separate database server.

Trade-off:
SQLite is suitable for this demonstration but has limitations for highly concurrent, distributed workloads.

### Pytest
Pytest is used to automate functional and edge-case testing.

## 3. Event History vs Current State

Two separate tables are maintained:

- customer_event_history: stores accepted historical events.
- customer_current: stores the latest state of each customer.

Keeping event history allows previous changes to be audited and current state to be reconstructed.

Trade-off:
Storing every event requires additional disk space.

## 4. Event Ordering

Events are ordered using:

(event_ts, source_seq)

This ensures deterministic processing when timestamps are equal, provided source_seq is unique within the relevant customer ordering.

Older events are retained in history but must not overwrite newer customer state.

## 5. Delete Handling

Deletes use soft-delete behavior.

Instead of physically removing a customer, the current-state record is marked as deleted.

A newer insert can reactivate a previously deleted customer.

Trade-off:
Soft deletes require additional filtering when querying active customers.

## 6. Duplicate Handling

event_id is used as the unique event identifier.

Database constraints prevent the same event from being inserted into history multiple times.

This supports safe reruns and duplicate detection.

## 7. Invalid Record Handling

Invalid records are stored separately in reject_events.

Each rejected record includes its source file, line number, processing run ID, and rejection reason.

This makes troubleshooting and auditing easier.

## 8. Transaction and Recovery Strategy

Each batch is processed transactionally.

If processing fails, database changes from the failed batch are rolled back.

Failure information is recorded separately so that failed executions remain observable.

Rerunning the same input should not create unintended duplicate events.

## 9. Performance Considerations

Initial implementation focuses on correctness and reliability.

Potential optimizations include:

- Batch database inserts using executemany.
- Indexing customer_id and event ordering columns.
- Rebuilding current state only for affected customers.
- Using SQLite WAL mode where appropriate.

Performance will be measured using different input sizes.

## 10. Future Improvements

For larger production workloads, the architecture could evolve to use:

- PostgreSQL for concurrent database workloads.
- Apache Spark for distributed data processing.
- Delta Lake for scalable historical data management.
- Kafka for streaming event ingestion.
- A dedicated dead-letter queue for rejected events.

## 11. Known Limitations

- The initial implementation runs locally.
- SQLite is not intended for distributed concurrent processing.
- External streaming services are not included.
- Performance depends on local hardware and storage.
