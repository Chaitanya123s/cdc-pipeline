
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


# Reproducible dataset
random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "large_customer_events.csv"

TOTAL_EVENTS = 100_000
TOTAL_CUSTOMERS = 20_000

FIELDS = [
    "event_id",
    "customer_id",
    "event_type",
    "event_timestamp",
    "customer_name",
    "run_id",
    "source_file",
    "source_seq",
]

EVENT_TYPES = ["INSERT", "UPDATE", "DELETE"]
NAMES = [
    "Amit Sharma",
    "Priya Patel",
    "Rahul Verma",
    "Sneha Gupta",
    "Arjun Kumar",
    "Neha Singh",
    "Rohan Mehta",
    "Ananya Rao",
]


def generate_dataset():
    base_time = datetime(
        2026, 1, 1, 9, 0, 0, tzinfo=timezone.utc
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for i in range(1, TOTAL_EVENTS + 1):
            customer_number = random.randint(1, TOTAL_CUSTOMERS)

            event_time = base_time + timedelta(seconds=i)

            writer.writerow({
                "event_id": f"PERF_EVT_{i:07d}",
                "customer_id": f"PERF_CUST_{customer_number:06d}",
                "event_type": random.choice(EVENT_TYPES),
                "event_timestamp": event_time.isoformat(),
                "customer_name": random.choice(NAMES),
                "run_id": "PERFORMANCE_RUN",
                "source_file": OUTPUT_FILE.name,
                "source_seq": i,
            })

    print("Dataset generated successfully!")
    print("Output:", OUTPUT_FILE)
    print("Total events:", TOTAL_EVENTS)
    print("Unique event IDs:", TOTAL_EVENTS)
    print("Random seed: 42")


if __name__ == "__main__":
    generate_dataset()
