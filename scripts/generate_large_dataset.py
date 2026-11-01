
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


# Reproducible random generator
rng = random.Random(42)

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
    if TOTAL_EVENTS < TOTAL_CUSTOMERS:
        raise ValueError("Events must be at least equal to customers.")

    base_time = datetime(
        2026, 1, 1, 9, 0, 0, tzinfo=timezone.utc
    )

    # Track whether each customer is currently deleted
    customer_deleted = {
        f"PERF_CUST_{i:06d}": False
        for i in range(1, TOTAL_CUSTOMERS + 1)
    }

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for i in range(1, TOTAL_EVENTS + 1):

            # First event for every customer must be INSERT
            if i <= TOTAL_CUSTOMERS:
                customer_id = f"PERF_CUST_{i:06d}"
                event_type = "INSERT"

            else:
                customer_id = rng.choice(
                    list(customer_deleted.keys())
                )

                if customer_deleted[customer_id]:
                    # A deleted customer can be reactivated
                    event_type = "INSERT"
                else:
                    event_type = rng.choices(
                        ["UPDATE", "DELETE"],
                        weights=[90, 10],
                        k=1
                    )[0]

            # Update customer lifecycle state
            if event_type == "DELETE":
                customer_deleted[customer_id] = True
            elif event_type == "INSERT":
                customer_deleted[customer_id] = False

            event_time = base_time + timedelta(seconds=i)

            writer.writerow({
                "event_id": f"PERF_EVT_{i:07d}",
                "customer_id": customer_id,
                "event_type": event_type,
                "event_timestamp": event_time.isoformat(),
                "customer_name": rng.choice(NAMES),
                "run_id": "PERFORMANCE_RUN",
                "source_file": OUTPUT_FILE.name,
                "source_seq": i,
            })

    print("Dataset generated successfully!")
    print("Output:", OUTPUT_FILE)
    print("Total events:", TOTAL_EVENTS)
    print("Total customers:", TOTAL_CUSTOMERS)
    print("Unique event IDs:", TOTAL_EVENTS)
    print("Random seed: 42")


if __name__ == "__main__":
    generate_dataset()
