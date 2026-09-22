#!/usr/bin/env python3
"""Systematic checks for data/benchmarks_collected.csv against a real
Dropbox folder listing, catching the exact bug class found during pilot
review: an agent finds the right document but assigns its content to the
wrong fiscal year (see docs/agent_playbook.md's "known failure mode").

Two deterministic checks, no LLM judgment involved:

1. PROVENANCE: does the row's cited source file actually exist in that
   plan's Dropbox folder? Catches a hallucinated or garbled citation.

2. SAME-YEAR-DOCUMENT-NOT-USED: does the plan's folder contain a document
   (especially an IPS, the most authoritative type) whose filename's own
   year token exactly equals the row's fiscal year, that ISN'T the row's
   cited source? If so, the row may be sourced from the wrong year's
   document even if the citation itself is genuine -- flag for review.

Requires an index CSV (ppd_id,filename,size_bytes) built from a real
mcp__Dropbox__list_folder call -- see data/dropbox_index/ for examples.
This script cannot call Dropbox itself; the index must be supplied.

Usage:
    python3 scripts/verify_batch.py data/dropbox_index/pilot_batch_1_index.csv
"""
import csv
import re
import sys
from collections import defaultdict

YEAR_RE = re.compile(r"(20[0-2]\d)")


def doc_type(filename: str) -> str:
    name = filename.lower()
    if "invpolstmt" in name:
        return "IPS"
    if "_av_" in name or name.startswith("av_") or "_av" in name.split("_")[-2:]:
        return "AV"
    return "CAFR"  # CAFR, ACFR, and *_air.pdf (Annual Investment Report) treated alike


def extract_year(filename: str) -> "int | None":
    years = YEAR_RE.findall(filename)
    if not years:
        return None
    # A filename can contain more than one year (e.g. a range like 1937-1942,
    # or an id suffix that happens to look like a year); take the first hit,
    # which in every observed naming convention is the document's own year.
    return int(years[0])


def load_index(path: str) -> dict:
    """Return {ppd_id: [(filename, doc_type, year, size), ...]}."""
    by_plan = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            fname = row["filename"]
            by_plan[row["ppd_id"]].append(
                (fname, doc_type(fname), extract_year(fname), int(row["size_bytes"]))
            )
    return by_plan


def base_filename(cited: str) -> str:
    """Records sometimes append descriptive text after the filename,
    e.g. "CA_..._2019_9.pdf.pdf, 'Portfolio Comparisons...' table" or
    "WI_..._2002_125.pdf.pdf (language cross-checked against ...)" --
    take just the leading filename token."""
    for sep in (",", ";", " ("):
        cited = cited.split(sep)[0]
    return cited.strip()


def check_row(row: dict, index: dict) -> list:
    findings = []
    ppd_id = row["ppd_id"]
    fy = int(float(row["fy"]))
    plan_files = index.get(ppd_id, [])
    plan_filenames = {f[0] for f in plan_files}

    for source_field in ("source_document_name", "returns_source_document_name"):
        cited = row.get(source_field, "").strip()
        if not cited:
            continue
        cited_base = base_filename(cited)
        if not plan_files:
            continue  # no index for this plan, can't check provenance
        if cited_base not in plan_filenames and "screenshot" not in row.get("notes", "").lower():
            findings.append(
                f"PROVENANCE: {source_field}={cited_base!r} not found in Dropbox index for ppd_id={ppd_id}"
            )

    cited_bases = {
        base_filename(row.get("source_document_name", "")),
        base_filename(row.get("returns_source_document_name", "")),
    }
    same_year_unused = [
        f for f in plan_files
        if f[2] == fy and f[0] not in cited_bases
    ]
    same_year_ips_unused = [f for f in same_year_unused if f[1] == "IPS"]
    if same_year_ips_unused and row.get("confidence") != "High":
        names = ", ".join(f[0] for f in same_year_ips_unused)
        findings.append(
            f"SAME-YEAR-IPS-NOT-USED: fy={fy} has an IPS file(s) [{names}] not cited "
            f"as this row's source (confidence={row.get('confidence')}) -- check whether "
            f"that document's content was misattributed to a different fiscal year"
        )
    return findings


def main(index_path: str) -> None:
    index = load_index(index_path)
    with open("data/benchmarks_collected.csv", newline="") as f:
        rows = list(csv.DictReader(f))

    plans_in_index = set(index.keys())
    rows_checked = [r for r in rows if r["ppd_id"] in plans_in_index]

    total_findings = 0
    for row in rows_checked:
        findings = check_row(row, index)
        for finding in findings:
            print(f"ppd_id={row['ppd_id']} PlanName={row['PlanName']} fy={row['fy']}: {finding}")
            total_findings += 1

    print(f"\nChecked {len(rows_checked)} rows across {len(plans_in_index)} plan(s) with an index.")
    print(f"Total findings: {total_findings}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
