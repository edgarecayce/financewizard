#!/usr/bin/env python3
"""Transform Schwab position exports into normalized portfolio data.

Usage:
  python tools/transform_schwab_positions.py \
    --portfolio ed-schwab-taxable \
    --input "portfolios/ed-schwab-taxable/imports/EC Main-Positions-2026-04-01-202522.csv"

If --input is omitted, the script picks the newest CSV in the portfolio imports folder.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional


EXCLUDED_ASSET_TYPES = {"Cash and Money Market", "Option"}
OUTPUT_COLUMNS = [
    "as_of_date",
    "ticker",
    "security_name",
    "asset_type",
    "total_quantity",
    "total_market_value",
    "total_cost_basis",
    "unrealized_gain",
    "weight_pct",
    "virtual_portfolio",
    "strategy_bucket",
    "thesis_id",
    "target_weight_pct",
    "status",
    "notes",
    "source_file",
]
OVERRIDE_COLUMNS = [
    "ticker",
    "virtual_portfolio",
    "strategy_bucket",
    "thesis_id",
    "target_weight_pct",
    "cost_basis_override",
    "status_override",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio", required=True)
    parser.add_argument("--input", help="Path to a specific Schwab CSV import")
    return parser.parse_args()


def parse_number(value: str) -> Optional[float]:
    if value is None:
        return None
    cleaned = value.strip().replace("$", "").replace(",", "")
    if cleaned in {"", "N/A", "Incomplete", "--"}:
        return None
    return float(cleaned)


def parse_percent(value: str) -> Optional[float]:
    if value is None:
        return None
    cleaned = value.strip().replace("%", "")
    if cleaned in {"", "N/A", "Incomplete", "--"}:
        return None
    return float(cleaned)


def parse_as_of_date(metadata_line: str, fallback_name: str) -> str:
    match = re.search(r"(\d{4}/\d{2}/\d{2})", metadata_line)
    if match:
        return datetime.strptime(match.group(1), "%Y/%m/%d").date().isoformat()

    name_match = re.search(r"(\d{4}-\d{2}-\d{2})", fallback_name)
    if name_match:
        return name_match.group(1)

    raise ValueError("Could not determine as_of_date from file metadata or filename")


def choose_input_file(imports_dir: Path) -> Path:
    csv_files = sorted(imports_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {imports_dir}")
    return csv_files[-1]


def load_overrides(overrides_path: Path) -> Dict[str, dict]:
    if not overrides_path.exists():
        return {}

    with overrides_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["ticker"].strip(): row for row in reader if row.get("ticker", "").strip()}


def load_rows(input_path: Path) -> tuple[str, Iterable[dict]]:
    raw_text = input_path.read_text(encoding="utf-8-sig")
    lines = [line for line in raw_text.splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError(f"Input file appears empty: {input_path}")

    metadata_line = lines[0]
    csv_text = "\n".join(lines[1:])
    reader = csv.DictReader(csv_text.splitlines())
    return metadata_line, reader


def transform_rows(reader: Iterable[dict], as_of_date: str, source_file: str, overrides: Dict[str, dict]) -> list[dict]:
    grouped: dict[str, dict] = {}

    for row in reader:
        ticker = (row.get("Symbol") or "").strip()
        security_name = (row.get("Description") or "").strip()
        asset_type = (row.get("Asset Type") or "").strip()

        if not ticker or ticker == "Positions Total":
            continue
        if asset_type in EXCLUDED_ASSET_TYPES:
            continue

        quantity = parse_number(row.get("Qty (Quantity)", "")) or 0.0
        market_value = parse_number(row.get("Mkt Val (Market Value)", ""))
        cost_basis = parse_number(row.get("Cost Basis", ""))
        weight_pct = parse_percent(row.get("% of Acct (% of Account)", ""))

        if ticker not in grouped:
            grouped[ticker] = {
                "as_of_date": as_of_date,
                "ticker": ticker,
                "security_name": security_name,
                "asset_type": asset_type,
                "total_quantity": 0.0,
                "total_market_value": 0.0,
                "cost_basis_values": [],
                "weight_pct": 0.0,
                "status_flags": set(),
                "notes": [],
                "source_file": source_file,
            }

        item = grouped[ticker]
        item["total_quantity"] += quantity
        if market_value is not None:
            item["total_market_value"] += market_value
        else:
            item["status_flags"].add("missing_market_value")
        if cost_basis is not None:
            item["cost_basis_values"].append(cost_basis)
        else:
            item["status_flags"].add("missing_cost_basis")
        if weight_pct is not None:
            item["weight_pct"] += weight_pct

    output_rows: list[dict] = []

    for ticker in sorted(grouped):
        item = grouped[ticker]
        override = overrides.get(ticker, {})

        total_cost_basis: Optional[float]
        if override.get("cost_basis_override", "").strip():
            total_cost_basis = float(override["cost_basis_override"].strip())
        elif item["cost_basis_values"]:
            total_cost_basis = sum(item["cost_basis_values"])
        else:
            total_cost_basis = None

        unrealized_gain = None
        if total_cost_basis is not None:
            unrealized_gain = item["total_market_value"] - total_cost_basis

        status = "incomplete" if item["status_flags"] else "untagged"
        if override.get("status_override", "").strip():
            status = override["status_override"].strip()

        notes = []
        if item["status_flags"]:
            notes.append("raw import has missing fields")
        if override.get("notes", "").strip():
            notes.append(override["notes"].strip())

        output_rows.append(
            {
                "as_of_date": as_of_date,
                "ticker": ticker,
                "security_name": item["security_name"],
                "asset_type": item["asset_type"],
                "total_quantity": format_decimal(item["total_quantity"]),
                "total_market_value": format_decimal(item["total_market_value"]),
                "total_cost_basis": format_decimal(total_cost_basis),
                "unrealized_gain": format_decimal(unrealized_gain),
                "weight_pct": format_decimal(item["weight_pct"]),
                "virtual_portfolio": override.get("virtual_portfolio", "untagged").strip() or "untagged",
                "strategy_bucket": override.get("strategy_bucket", "").strip(),
                "thesis_id": override.get("thesis_id", "").strip(),
                "target_weight_pct": override.get("target_weight_pct", "").strip(),
                "status": status,
                "notes": "; ".join(notes),
                "source_file": source_file,
            }
        )

    return output_rows


def format_decimal(value: Optional[float]) -> str:
    if value is None:
        return ""
    rounded = round(value, 4)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def ensure_override_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OVERRIDE_COLUMNS)
        writer.writeheader()


def main() -> None:
    args = parse_args()

    portfolio_root = Path("portfolios") / args.portfolio
    imports_dir = portfolio_root / "imports"
    normalized_dir = portfolio_root / "normalized"
    input_path = Path(args.input) if args.input else choose_input_file(imports_dir)

    overrides_path = normalized_dir / "position-overrides.csv"
    ensure_override_file(overrides_path)
    overrides = load_overrides(overrides_path)

    metadata_line, reader = load_rows(input_path)
    as_of_date = parse_as_of_date(metadata_line, input_path.name)
    rows = transform_rows(reader, as_of_date, input_path.name, overrides)

    output_path = normalized_dir / "positions.csv"
    write_csv(output_path, rows)
    print(f"Wrote {len(rows)} normalized rows to {output_path}")


if __name__ == "__main__":
    main()
