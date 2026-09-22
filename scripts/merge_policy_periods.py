#!/usr/bin/env python3
"""Expand agent-found policy periods into per-fiscal-year rows and merge into
data/benchmarks_collected.csv, updating data/worklist.csv status as it goes.

Usage:
    python3 scripts/merge_policy_periods.py path/to/periods_batch.json BATCH_NAME

`periods_batch.json` must be a JSON list of period objects shaped as
described in docs/agent_playbook.md.
"""
import csv
import json
import os
import sys
from datetime import date

OUTPUT_COLUMNS = [
    "ppd_id", "PlanName", "StateAbbrev", "fy",
    "policy_period_start", "policy_period_end",
    "total_fund_benchmark", "us_equity_benchmark", "intl_equity_benchmark",
    "global_equity_benchmark", "fixed_income_benchmark", "real_estate_benchmark",
    "private_equity_benchmark", "hedge_fund_absolute_return_benchmark",
    "real_assets_commodities_benchmark", "cash_benchmark", "other_asset_classes_notes",
    "source_type", "source_document_name", "source_url", "source_document_fy",
    "confidence", "researcher", "research_date", "notes",
]

WORKLIST_PATH = "data/worklist.csv"
OUTPUT_PATH = "data/benchmarks_collected.csv"


def load_worklist():
    with open(WORKLIST_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def save_worklist(rows, fieldnames):
    with open(WORKLIST_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_existing_output():
    if not os.path.exists(OUTPUT_PATH):
        return []
    with open(OUTPUT_PATH, newline="") as f:
        return list(csv.DictReader(f))


def main(periods_path: str, batch_name: str) -> None:
    with open(periods_path) as f:
        periods = json.load(f)

    worklist_rows = load_worklist()
    worklist_fields = list(worklist_rows[0].keys()) if worklist_rows else []
    by_plan_fy = {}
    for row in worklist_rows:
        by_plan_fy[(int(float(row["ppd_id"])), int(float(row["fy"])))] = row

    existing = load_existing_output()
    existing_keys = {(r["ppd_id"], r["fy"]) for r in existing}

    today = date.today().isoformat()
    new_rows = []
    touched = 0

    for period in periods:
        ppd_id = period["ppd_id"]
        start = int(period["policy_period_start"])
        end = int(period["policy_period_end"])
        for fy in range(start, end + 1):
            key = (str(ppd_id), str(fy))
            wl_key = (int(ppd_id), int(fy))
            if wl_key not in by_plan_fy:
                continue  # fiscal year outside the worklist's range for this plan
            if key in existing_keys:
                continue  # already recorded, don't duplicate
            wl_row = by_plan_fy[wl_key]
            record = {col: period.get(col, "") for col in OUTPUT_COLUMNS}
            record.update({
                "ppd_id": wl_row["ppd_id"],
                "PlanName": wl_row["PlanName"],
                "StateAbbrev": wl_row["StateAbbrev"],
                "fy": wl_row["fy"],
                "researcher": batch_name,
                "research_date": today,
            })
            new_rows.append(record)
            existing_keys.add(key)
            wl_row["status"] = "done"
            wl_row["batch"] = batch_name
            touched += 1

    all_rows = existing + new_rows
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    if worklist_fields:
        save_worklist(worklist_rows, worklist_fields)

    print(f"Added {touched} new plan-year rows from {len(periods)} policy period(s).")
    print(f"data/benchmarks_collected.csv now has {len(all_rows)} rows total.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
