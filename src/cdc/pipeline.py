
import uuid
import logging
from pathlib import Path

from src.cdc.db import (
    initialize_database,
    process_event,
    start_pipeline_run,
    finish_pipeline_run,
    save_rejected_records,
)
from src.cdc.ingestion import ingest_csv
from src.cdc.reconciliation import generate_reconciliation_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "reports"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_pipeline(file_path):
    file_path = Path(file_path)

    run_id = f"RUN_{uuid.uuid4().hex[:12].upper()}"

    total_records = 0
    processed_records = 0
    rejected_records = 0
    skipped_records = 0

    processing_rejections = []
    started = False

    try:
        initialize_database()

        start_pipeline_run(
            run_id,
            file_path.name,
            total_records=0,
        )
        started = True

        logger.info("Pipeline started: %s", run_id)

        valid_events, rejected_events = ingest_csv(
            file_path,
            run_id=run_id,
        )

        rejected_records = len(rejected_events)
        total_records = len(valid_events) + rejected_records

        for event in valid_events:
            try:
                result = process_event(event)

                if result:
                    processed_records += 1
                else:
                    skipped_records += 1

            except Exception as error:
                rejected_records += 1

                processing_rejections.append({
                    "row_number": None,
                    "record": event,
                    "reason": str(error),
                })

                logger.exception(
                    "Event processing failed: %s",
                    event.get("event_id"),
                )

        if processing_rejections:
            save_rejected_records(
                processing_rejections,
                default_run_id=run_id,
                default_source_file=file_path.name,
            )

        status = "PARTIAL" if rejected_records > 0 else "SUCCESS"

        finish_pipeline_run(
            run_id=run_id,
            status=status,
            total_records=total_records,
            processed_records=processed_records,
            rejected_records=rejected_records,
            skipped_records=skipped_records,
        )

        logger.info("Pipeline completed: %s", run_id)

    except Exception as error:
        logger.exception("Pipeline failed: %s", run_id)

        if started:
            finish_pipeline_run(
                run_id=run_id,
                status="FAILED",
                total_records=total_records,
                processed_records=processed_records,
                rejected_records=rejected_records,
                skipped_records=skipped_records,
                failure_reason=str(error),
            )

        raise

    summary = {
        "run_id": run_id,
        "source_file": file_path.name,
        "total_records": total_records,
        "processed_records": processed_records,
        "rejected_records": rejected_records,
        "skipped_records": skipped_records,
        "status": status,
    }

    reconciliation_report = generate_reconciliation_report(summary)

    summary["reconciliation"] = reconciliation_report

    print("\nPIPELINE RUN SUMMARY:")
    print(summary)

    return summary


if __name__ == "__main__":
    input_file = PROJECT_ROOT / "data" / "raw" / "customer_events.csv"
    run_pipeline(input_file)
