
from pathlib import Path
import json
from datetime import datetime, timezone


def reconcile_counts(total_records, processed_records,
                     rejected_records, skipped_records):

    accounted_records = (
        processed_records + rejected_records + skipped_records
    )

    return {
        "total_records": total_records,
        "processed_records": processed_records,
        "rejected_records": rejected_records,
        "skipped_records": skipped_records,
        "accounted_records": accounted_records,
        "unaccounted_records": total_records - accounted_records,
        "reconciliation_passed": total_records == accounted_records,
    }


def generate_reconciliation_report(summary):
    report = reconcile_counts(
        total_records=summary["total_records"],
        processed_records=summary["processed_records"],
        rejected_records=summary["rejected_records"],
        skipped_records=summary["skipped_records"],
    )

    report["run_id"] = summary["run_id"]
    report["generated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    project_root = Path(__file__).resolve().parents[2]
    report_dir = project_root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"reconciliation_{summary['run_id']}.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("Reconciliation report generated:", report_path)
    print("Reconciliation passed:", report["reconciliation_passed"])

    return report
