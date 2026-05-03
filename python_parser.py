"""
python_parser.py
Reads cdc_fall_stats.csv and prints a summary of fall statistics.
Usage: python python_parser.py [path_to_csv]
"""

import csv
import sys
from collections import defaultdict


def load_csv(filepath: str) -> list[dict]:
    """Load CSV file and return list of row dicts."""
    rows = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)
    except PermissionError:
        print(f"[ERROR] Permission denied: {filepath}")
        sys.exit(1)
    return rows


def parse_row(row: dict) -> dict | None:
    """Convert raw string values to correct types. Returns None on bad row."""
    try:
        return {
            "year": int(row["year"]),
            "state": row["state"].strip(),
            "falls_per_100k": float(row["falls_per_100k"]),
            "hospitalization_rate": float(row["hospitalization_rate"]),
            "avg_cost_usd": float(row["avg_cost_usd"]),
        }
    except (ValueError, KeyError) as e:
        print(f"[WARNING] Skipping malformed row {row}: {e}")
        return None


def compute_summary(records: list[dict]) -> dict:
    """Aggregate key statistics across all records."""
    if not records:
        return {}

    # Group by year for trend analysis
    by_year = defaultdict(list)
    for r in records:
        by_year[r["year"]].append(r)

    total_falls = sum(r["falls_per_100k"] for r in records)
    avg_falls = total_falls / len(records)
    avg_cost = sum(r["avg_cost_usd"] for r in records) / len(records)
    avg_hosp = sum(r["hospitalization_rate"] for r in records) / len(records)

    # Highest-risk state overall
    highest = max(records, key=lambda r: r["falls_per_100k"])
    lowest = min(records, key=lambda r: r["falls_per_100k"])

    # Per-year averages
    yearly_avg = {}
    for year, rows in sorted(by_year.items()):
        yearly_avg[year] = sum(r["falls_per_100k"] for r in rows) / len(rows)

    return {
        "total_records": len(records),
        "avg_falls_per_100k": round(avg_falls, 1),
        "avg_hospitalization_rate": round(avg_hosp, 1),
        "avg_cost_usd": round(avg_cost, 0),
        "highest_risk": highest,
        "lowest_risk": lowest,
        "yearly_averages": yearly_avg,
    }


def print_summary(summary: dict) -> None:
    """Print formatted summary to stdout."""
    print("=" * 50)
    print("  CDC FALL STATISTICS — SUMMARY REPORT")
    print("=" * 50)
    print(f"  Total records loaded : {summary['total_records']}")
    print(f"  Avg falls / 100k     : {summary['avg_falls_per_100k']}")
    print(f"  Avg hospitalization% : {summary['avg_hospitalization_rate']}")
    print(f"  Avg cost (USD)       : ${summary['avg_cost_usd']:,.0f}")
    print()
    print("  Highest-risk entry:")
    h = summary["highest_risk"]
    print(f"    {h['state']} ({h['year']}) — {h['falls_per_100k']} falls/100k")
    print()
    print("  Lowest-risk entry:")
    lo = summary["lowest_risk"]
    print(f"    {lo['state']} ({lo['year']}) — {lo['falls_per_100k']} falls/100k")
    print()
    print("  Year-over-year avg falls/100k:")
    for year, avg in summary["yearly_averages"].items():
        print(f"    {year}: {avg:.1f}")
    print("=" * 50)


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "cdc_fall_stats.csv"
    print(f"[INFO] Loading: {filepath}")

    raw_rows = load_csv(filepath)
    records = [r for row in raw_rows if (r := parse_row(row)) is not None]
    print(f"[INFO] Parsed {len(records)}/{len(raw_rows)} rows successfully.")

    summary = compute_summary(records)
    print_summary(summary)


if __name__ == "__main__":
    main()
