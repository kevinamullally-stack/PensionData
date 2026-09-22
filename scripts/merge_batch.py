#!/usr/bin/env python3
"""Merge one or two independent research passes for a plan into
data/benchmarks_collected.csv, reconciling field-by-field when two passes
are given (a cross-model check: two different models independently research
the same plan; agreement is trusted, disagreement is flagged for review).

Each pass is a JSON file shaped as {"policy_periods": [...], "annual_returns": [...]}
per docs/agent_playbook.md's "Output format" section.

Usage (single pass, no cross-check):
    python3 scripts/merge_batch.py pass_a.json BATCH_NAME_A

Usage (two independent model passes, reconciled):
    python3 scripts/merge_batch.py pass_a.json BATCH_NAME_A pass_b.json BATCH_NAME_B
"""
import csv
import json
import os
import sys
from datetime import date

COMPOSITION_FIELDS = [
    "total_fund_benchmark", "us_equity_benchmark", "intl_equity_benchmark",
    "global_equity_benchmark", "fixed_income_benchmark", "real_estate_benchmark",
    "private_equity_benchmark", "hedge_fund_absolute_return_benchmark",
    "real_assets_commodities_benchmark", "cash_benchmark", "other_asset_classes_notes",
]
COMPOSITION_SOURCE_FIELDS = [
    "source_type", "source_document_name", "source_url", "source_document_fy",
    "source_page", "source_quote", "confidence",
]
RETURNS_ASSET_CLASSES = [
    "us_equity", "intl_equity", "global_equity", "fixed_income", "real_estate",
    "private_equity", "hedge_fund_absolute_return", "real_assets_commodities", "cash",
]
RETURNS_FIELDS = (
    ["total_fund_actual_return_pct", "total_fund_benchmark_return_pct"]
    + [f"{cls}_actual_return_pct" for cls in RETURNS_ASSET_CLASSES]
    + [f"{cls}_benchmark_return_pct" for cls in RETURNS_ASSET_CLASSES]
    + ["other_returns_notes"]
)
RETURNS_SOURCE_FIELDS = [
    "returns_source_type", "returns_source_document_name", "returns_source_url",
    "returns_source_document_fy", "returns_source_page", "returns_source_quote",
    "returns_confidence",
]
NUMERIC_RETURNS_FIELDS = tuple(
    f for f in RETURNS_FIELDS if f.endswith("_return_pct")
)

OUTPUT_COLUMNS = (
    ["ppd_id", "PlanName", "StateAbbrev", "fy", "policy_period_start", "policy_period_end"]
    + COMPOSITION_FIELDS + COMPOSITION_SOURCE_FIELDS
    + RETURNS_FIELDS + RETURNS_SOURCE_FIELDS
    + ["cross_model_agreement", "researcher", "research_date", "notes"]
)

WORKLIST_PATH = "data/worklist.csv"
OUTPUT_PATH = "data/benchmarks_collected.csv"


def norm(v):
    if v is None:
        return ""
    return " ".join(str(v).split()).strip().lower()


def numeric_close(a, b, tol=0.05):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return norm(a) == norm(b)


def expand_composition(policy_periods, worklist_keys):
    out = {}
    for period in policy_periods:
        ppd_id = int(float(period["ppd_id"]))
        start = int(period["policy_period_start"])
        end = int(period["policy_period_end"])
        for fy in range(start, end + 1):
            if (ppd_id, fy) not in worklist_keys:
                continue
            row = {f: period.get(f, "") for f in COMPOSITION_FIELDS + COMPOSITION_SOURCE_FIELDS}
            row["policy_period_start"] = start
            row["policy_period_end"] = end
            out[(ppd_id, fy)] = row
    return out


def expand_returns(annual_returns, worklist_keys):
    out = {}
    for r in annual_returns:
        ppd_id = int(float(r["ppd_id"]))
        fy = int(r["fy"])
        if (ppd_id, fy) not in worklist_keys:
            continue
        out[(ppd_id, fy)] = {f: r.get(f, "") for f in RETURNS_FIELDS + RETURNS_SOURCE_FIELDS}
    return out


def reconcile(dict_a, dict_b, fields, numeric_fields=()):
    """Return {key: (merged_row, agreement, mismatch_note)}."""
    result = {}
    for key in set(dict_a) | set(dict_b):
        a, b = dict_a.get(key), dict_b.get(key)
        if a and not b:
            result[key] = (a, "single-pass-only", "")
            continue
        if b and not a:
            result[key] = (b, "single-pass-only", "")
            continue
        merged, mismatches = {}, []
        for f in fields:
            va, vb = a.get(f, ""), b.get(f, "")
            if not va:
                merged[f] = vb
            elif not vb:
                merged[f] = va
            else:
                is_close = numeric_close(va, vb) if f in numeric_fields else norm(va) == norm(vb)
                merged[f] = va
                if not is_close:
                    mismatches.append(f"{f}: A={va!r} vs B={vb!r}")
        result[key] = (merged, "disagree" if mismatches else "agree", "; ".join(mismatches))
    return result


def load_worklist():
    with open(WORKLIST_PATH, newline="") as f:
        return list(csv.DictReader(f))


def save_worklist(rows, fieldnames):
    with open(WORKLIST_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_existing_output():
    if not os.path.exists(OUTPUT_PATH):
        return {}
    with open(OUTPUT_PATH, newline="") as f:
        return {(r["ppd_id"], r["fy"]): r for r in csv.DictReader(f)}


def main():
    args = sys.argv[1:]
    if len(args) not in (2, 4):
        print(__doc__)
        sys.exit(1)

    pass_a_path, batch_a = args[0], args[1]
    pass_b_path, batch_b = (args[2], args[3]) if len(args) == 4 else (None, None)

    with open(pass_a_path) as f:
        data_a = json.load(f)

    worklist_rows = load_worklist()
    worklist_fields = list(worklist_rows[0].keys())
    worklist_by_key = {(int(float(r["ppd_id"])), int(float(r["fy"]))): r for r in worklist_rows}
    worklist_keys = set(worklist_by_key)

    comp_a = expand_composition(data_a.get("policy_periods", []), worklist_keys)
    ret_a = expand_returns(data_a.get("annual_returns", []), worklist_keys)

    if pass_b_path:
        with open(pass_b_path) as f:
            data_b = json.load(f)
        comp_b = expand_composition(data_b.get("policy_periods", []), worklist_keys)
        ret_b = expand_returns(data_b.get("annual_returns", []), worklist_keys)
        comp_reconciled = reconcile(comp_a, comp_b, COMPOSITION_FIELDS + COMPOSITION_SOURCE_FIELDS)
        ret_reconciled = reconcile(ret_a, ret_b, RETURNS_FIELDS + RETURNS_SOURCE_FIELDS, NUMERIC_RETURNS_FIELDS)
        researcher = f"{batch_a}+{batch_b}"
    else:
        comp_reconciled = {k: (v, "single-pass-only", "") for k, v in comp_a.items()}
        ret_reconciled = {k: (v, "single-pass-only", "") for k, v in ret_a.items()}
        researcher = batch_a

    existing = load_existing_output()
    today = date.today().isoformat()
    touched = 0

    for key in set(comp_reconciled) | set(ret_reconciled):
        ppd_id, fy = key
        wl_row = worklist_by_key[key]
        str_key = (str(ppd_id), str(fy))
        row = existing.get(str_key) or {col: "" for col in OUTPUT_COLUMNS}
        row["ppd_id"] = str(ppd_id)
        row["PlanName"] = wl_row["PlanName"]
        row["StateAbbrev"] = wl_row["StateAbbrev"]
        row["fy"] = str(fy)

        agreements, notes_parts = [], [row["notes"]] if row.get("notes") else []

        if key in comp_reconciled:
            merged, agreement, mismatch_note = comp_reconciled[key]
            row.update(merged)
            agreements.append(agreement)
            if mismatch_note:
                notes_parts.append(f"[composition {agreement}] {mismatch_note}")

        if key in ret_reconciled:
            merged, agreement, mismatch_note = ret_reconciled[key]
            row.update(merged)
            agreements.append(agreement)
            if mismatch_note:
                notes_parts.append(f"[returns {agreement}] {mismatch_note}")

        row["cross_model_agreement"] = (
            "disagree" if "disagree" in agreements
            else "single-pass-only" if "single-pass-only" in agreements
            else "agree"
        )
        row["researcher"] = researcher
        row["research_date"] = today
        row["notes"] = " | ".join(p for p in notes_parts if p)

        existing[str_key] = row
        wl_row["status"] = "done"
        wl_row["batch"] = researcher
        touched += 1

    all_rows = list(existing.values())
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    save_worklist(worklist_rows, worklist_fields)

    disagreements = sum(1 for r in all_rows if r.get("cross_model_agreement") == "disagree")
    print(f"Upserted {touched} plan-year rows ({researcher}).")
    print(f"data/benchmarks_collected.csv now has {len(all_rows)} rows total.")
    print(f"Rows flagged 'disagree' needing manual review: {disagreements}")


if __name__ == "__main__":
    main()
