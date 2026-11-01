
import json
import time
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cdc.pipeline import run_pipeline


INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "large_customer_events.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_benchmark():
    print("Starting CDC performance benchmark...")
    print("Input file:", INPUT_FILE)

    start_time = time.perf_counter()

    summary = run_pipeline(INPUT_FILE)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    total_records = summary["total_records"]

    events_per_second = (
        total_records / execution_time
        if execution_time > 0 else 0
    )

    benchmark_report = {
        "benchmark_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_file": INPUT_FILE.name,
        "total_records": total_records,
        "processed_records": summary["processed_records"],
        "rejected_records": summary["rejected_records"],
        "skipped_records": summary["skipped_records"],
        "execution_time_seconds": round(execution_time, 3),
        "events_per_second": round(events_per_second, 2),
        "pipeline_status": summary["status"],
        "reconciliation_passed": summary["reconciliation"][
            "reconciliation_passed"
        ],
    }

    report_path = REPORT_DIR / "performance_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(benchmark_report, file, indent=4)

    print("\nPERFORMANCE BENCHMARK RESULTS")
    print("--------------------------------")
    for key, value in benchmark_report.items():
        print(f"{key}: {value}")

    print("\nPerformance report saved:", report_path)


if __name__ == "__main__":
    run_benchmark()
