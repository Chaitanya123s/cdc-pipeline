# AI Prompt History

This document records the AI interactions used during the development of the Customer Change Data Capture (CDC) Pipeline.

The prompts are organized by development phase to demonstrate the problem-solving approach, technical discussions, implementation decisions, and validation activities throughout the project.

---

## 1. Project Planning and Requirement Analysis

**AI Tool:** ChatGPT

**Objective:** Analyze the assignment requirements and establish a practical development approach.

**Prompt:**

I have received a Data Engineering assignment that requires developing a reliable data pipeline within a 72-hour submission window.

I want to understand the requirements before beginning implementation. Analyze the assignment and identify the essential deliverables, technical requirements, evaluation criteria, and potential challenges.

Pay particular attention to data quality, schema validation, duplicate handling, idempotency, error handling, automated testing, reconciliation, performance measurement, and documentation.

Recommend a suitable technology stack that allows me to build a complete, locally executable solution without unnecessary infrastructure.

Explain the reasoning behind your recommendations and organize the work into manageable development phases.

**Expected Outcome:**
A clear understanding of the assignment scope, technical requirements, project priorities, and implementation strategy.

---

## 2. Architecture and Technical Design

**AI Tool:** Claude Code

**Objective:** Design a modular Customer Change Data Capture pipeline.

**Prompt:**

Act as a Senior Data Engineer and help me design a Customer Change Data Capture (CDC) pipeline using Python and SQLite.

The pipeline should process customer Insert (I), Update (U), and Delete (D) events from input files.

The system must maintain two important data representations:

1. An event history table that preserves accepted customer changes.
2. A current-state table that represents the latest valid state of each customer.

Design a modular architecture covering:

- Input file reading and parsing.
- Schema validation and business-rule validation.
- Reference data validation.
- Duplicate event detection.
- Event ordering using event timestamps and source sequence numbers.
- Late-arriving and out-of-order event handling.
- Historical event storage.
- Current-state reconstruction.
- Invalid record quarantine.
- Transaction management and recovery.
- Operational logging and pipeline run tracking.
- Data reconciliation and reporting.

Use a dedicated customer reference table to demonstrate referential integrity.

Define the database tables, primary keys, foreign keys, important constraints, and relationships.

Use deterministic event processing so that processing the same input multiple times does not create unintended duplicates.

Keep the architecture simple, modular, maintainable, and suitable for a local demonstration.

Provide a phased implementation plan, recommended directory structure, business assumptions, edge cases, and testing requirements.

Explain the reasoning behind important design decisions rather than simply listing implementation tasks.

**Expected Outcome:**
A structured CDC architecture, database design, processing strategy, and phased implementation roadmap.

---

## 3. Architecture Review and Technical Improvements

**AI Tool:** ChatGPT

**Objective:** Review the proposed architecture against the assignment requirements.

**Prompt:**

I have a proposed implementation plan for my Customer CDC Pipeline.

Review the architecture critically from a Data Engineering perspective.

Check whether the proposed design correctly handles event ordering, duplicate detection, late-arriving events, idempotency, database transactions, rollback, retry, schema changes, and data reconciliation.

Identify technical weaknesses and missing acceptance criteria.

Pay special attention to the following:

- Whether historical event storage and current-state management remain consistent.
- Whether older events can incorrectly overwrite newer customer records.
- Whether duplicate events are prevented at the database level.
- Whether failed transactions can be retried safely.
- Whether run-level operational metrics are accurate.
- Whether rejected records remain traceable to their source files.

Recommend practical improvements while avoiding unnecessary architectural complexity.

**Expected Outcome:**
An improved technical design with clearly identified risks, assumptions, and corrective recommendations.

---

## 4. Development Environment and Project Structure

**AI Tool:** ChatGPT

**Objective:** Set up a clean and reproducible local development environment.

**Prompt:**

Guide me through setting up the Customer CDC Pipeline project using Python, VS Code, and Windows PowerShell.

I want to create a modular directory structure separating source code, documentation, scripts, sample data, expected outputs, tests, and reports.

Guide me through:

- Creating the project directory.
- Checking the Python installation.
- Creating and activating a virtual environment.
- Preparing the dependency file.
- Creating the initial documentation files.
- Initializing Git.
- Configuring .gitignore.
- Creating meaningful initial commits.

Explain the purpose of each command and directory.

Proceed incrementally and verify each step before moving forward. Do not skip steps or assume that a command succeeded without checking its output.

**Expected Outcome:**
A properly configured local development environment with a structured project repository and version control.

---

## 5. Documentation and Data Modeling

**AI Tool:** ChatGPT

**Objective:** Prepare project documentation and define database structures.

**Prompt:**

Help me prepare professional technical documentation for my Customer CDC Pipeline.

I need to create:

1. README.md covering the project overview, objectives, architecture, technology stack, setup instructions, execution steps, assumptions, and limitations.
2. data_dictionary.md documenting each database table, column, data type, nullability, constraints, and business meaning.
3. design_tradeoffs.md explaining technology selection, event history, current-state reconstruction, soft deletes, event ordering, idempotency, and future improvements.
4. ai_usage.md documenting AI assistance and my review responsibilities.
5. prompt_history.md recording the prompts used throughout development.

Use consistent snake_case naming conventions, ISO-8601 UTC timestamps, and explicit run_id and source_file fields where appropriate.

Ensure that the documentation reflects the proposed design and does not claim that unimplemented functionality has already been completed.

**Expected Outcome:**
Consistent technical documentation describing the project architecture, data model, design decisions, and development process.

---

## 6. Core Pipeline Implementation

**AI Tool:** Claude Code

**Objective:** Implement the CDC pipeline using modular Python components.

**Prompt:**

Implement the Customer CDC Pipeline according to the approved architecture.

Use separate modules for database management, input reading, validation, event loading, operational logging, reconciliation, and command-line execution.

The implementation must:

- Read customer events from input files.
- Validate required fields and expected data types.
- Validate operation types and timestamps.
- Check customer region codes against reference data.
- Quarantine invalid records with traceable rejection reasons.
- Prevent duplicate event insertion.
- Preserve accepted event history.
- Reconstruct the current customer state using deterministic event ordering.
- Handle soft deletes and newer insert events after deletion.
- Maintain processing run metadata and operational metrics.

Use appropriate database constraints and transactions.

Keep functions focused, provide meaningful error handling, and explain important implementation decisions.

Implement incrementally and provide instructions for validating each module.

**Expected Outcome:**
A modular, executable CDC pipeline with validation, event processing, historical storage, and current-state management.

---

## 7. Data Generation and Test Scenarios

**AI Tool:** Claude Code

**Objective:** Generate reproducible sample data covering normal and exceptional cases.

**Prompt:**

Develop a reproducible synthetic data generator for the CDC pipeline.

Use a fixed random seed so that generated data can be recreated consistently.

Support configurable customer and event counts, including a larger execution with at least 100,000 events where practical.

Include:

- Normal insert, update, and delete sequences.
- Duplicate event identifiers.
- Missing required fields.
- Invalid timestamps.
- Unknown region codes.
- Invalid operation types.
- Malformed records.
- Unexpected schema changes.
- Equal event timestamps.
- Out-of-order events.
- Late-arriving records.
- Boundary values and empty input batches.

Keep expected-answer labels and expected final-state results separate from input data.

Also provide a small human-readable sample dataset for quick manual verification.

**Expected Outcome:**
A reproducible synthetic dataset and clearly separated expected results for pipeline validation.

---

## 8. Automated Testing and Error Handling

**AI Tool:** ChatGPT and Claude Code

**Objective:** Verify pipeline correctness across normal and negative scenarios.

**Prompt:**

Review the CDC pipeline and develop automated tests using pytest.

Cover the following scenarios:

- Successful insert, update, and delete processing.
- Empty input.
- Malformed input records.
- Missing required fields and null values.
- Duplicate event identifiers.
- Invalid reference keys.
- Unexpected input schema changes.
- Equal timestamps with source sequence ordering.
- Out-of-order event processing.
- Late updates arriving after a delete.
- Newer inserts that reactivate deleted customers.
- Reprocessing the same input file.
- Partial failure, transaction rollback, and retry.
- Input-order independence.

For every test, explain the expected behavior and assert the resulting database state.

Do not rely only on checking whether functions execute without errors. Verify the actual stored records and business outcomes.

**Expected Outcome:**
An automated test suite demonstrating data correctness, edge-case handling, and recovery behavior.

---

## 9. Reconciliation and Data Quality

**AI Tool:** ChatGPT

**Objective:** Demonstrate that source and target datasets are consistent.

**Prompt:**

Help me develop a reconciliation module for the Customer CDC Pipeline.

I want to verify:

- Source input count against accepted, duplicate, and rejected counts.
- Accepted event counts against historical event records.
- Uniqueness of customer primary keys.
- Correct current-state records based on the latest accepted event.
- Referential integrity against the region reference table.
- Traceability of rejected records.
- Consistency between actual output and separately generated expected results.

Provide appropriate SQL queries and Python assertions.

Generate a readable validation report showing successful checks and failures.

Ensure that reconciliation failures are clearly reported rather than silently ignored.

**Expected Outcome:**
A reproducible reconciliation report demonstrating the correctness and consistency of pipeline outputs.

---

## 10. Performance Measurement and Optimization

**AI Tool:** Claude Code and ChatGPT

**Objective:** Measure processing performance and identify a practical optimization.

**Prompt:**

Help me evaluate the performance of my CDC pipeline using reproducible test runs.

Measure execution time and records processed per second for different input sizes, such as 10,000, 100,000, and 500,000 events where practical.

Explain how to perform fair comparisons using the same hardware, dataset, and processing conditions.

Identify one reasonable optimization, such as batch database insertion, appropriate indexing, or rebuilding current state only for affected customers.

Measure performance before and after the optimization.

Record actual execution results in a performance report. Do not invent benchmark values or claim improvements without evidence.

**Expected Outcome:**
A performance report containing actual measurements, comparisons, and an explanation of the selected optimization.

---

## 11. Debugging and Code Review

**AI Tool:** Claude Code and ChatGPT

**Objective:** Identify implementation issues and improve code quality.

**Prompt:**

Review the current CDC pipeline implementation for correctness, maintainability, and reliability.

Examine Python functions, SQL queries, database constraints, exception handling, transaction boundaries, and logging.

Identify potential bugs, duplicated logic, inefficient operations, and missing edge cases.

When an error occurs, explain the underlying cause and provide a targeted correction rather than replacing large sections of working code unnecessarily.

After making a correction, suggest appropriate tests to verify that the issue has been resolved without introducing regressions.

**Expected Outcome:**
Improved code quality, understandable debugging decisions, and verified corrections.

---

## 12. Final Submission Review

**AI Tool:** ChatGPT

**Objective:** Verify project completeness before submitting to YottaFlex AI.

**Prompt:**

Perform a final technical review of my completed Customer CDC Pipeline against the YottaFlex AI assignment requirements.

Evaluate:

- Project architecture and source code organization.
- Data validation and business-rule enforcement.
- Duplicate handling and idempotency.
- Event ordering and late-arriving data.
- Transaction recovery and retry behavior.
- Operational logging and metrics.
- Automated test coverage.
- Reconciliation results.
- Performance measurements.
- README and data dictionary.
- Sample input and output datasets.
- Design and trade-off documentation.
- AI usage disclosure and prompt history.
- GitHub repository structure and execution instructions.

Identify any missing requirements, unsupported claims, incomplete implementation areas, or potential submission risks.

Provide a final checklist based on actual project files and execution evidence.

Do not assume that tests pass or functionality works unless the corresponding evidence is available.

**Expected Outcome:**
A final submission-readiness assessment covering technical correctness, reproducibility, documentation, and transparency.

---

## 13. AI Usage and Accountability

AI tools were used as technical assistants for planning, design discussions, implementation guidance, debugging, and documentation.

The prompts are organized by development phase to provide visibility into how AI assistance contributed to the project.

I remain responsible for reviewing the generated suggestions, understanding the technical implementation, executing tests, validating the outputs, and explaining the final engineering decisions.

The final submission will reflect the actual implementation and verification results rather than unverified AI-generated claims.