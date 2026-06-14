"""Run offline coordinate plausibility auditing for U.S. military site CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.coordinate_audit import (  # noqa: E402
    audit_us_military_records,
    summarize_audit_results,
)
from src.data.load_locations import read_csv_robust  # noqa: E402
from src.data.normalize_us_military import normalize_us_military_row  # noqa: E402
from src.data.schemas import LocationRecord  # noqa: E402


def _load_records(path: Path) -> list[LocationRecord]:
    read_result = read_csv_robust(path)
    records: list[LocationRecord] = []
    for index, row in read_result.frame.iterrows():
        row_number = int(index) + 2
        normalized = normalize_us_military_row(
            {column: row.get(column, "") for column in read_result.frame.columns},
            row_number,
        )
        records.append(normalized.record)
    return records


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/us_military_sites.csv"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/us_military_coordinate_audit.csv"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("artifacts/us_military_coordinate_audit_summary.json"),
    )
    return parser.parse_args()


def main() -> None:
    """Run the audit and write artifacts."""

    args = parse_args()
    records = _load_records(args.input)
    results = audit_us_military_records(records)
    summary = summarize_audit_results(results)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].to_dict()) if results else [])
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_dict())

    args.summary_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(f"Audited {summary['total']:,} records")
    print(f"By status: {summary['by_status']}")
    print(f"By severity: {summary['by_severity']}")
    print(f"By reason: {summary['by_reason']}")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.summary_output}")


if __name__ == "__main__":
    main()
