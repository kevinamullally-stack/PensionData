# Collection progress log

Total worklist: 4,000 plan-year rows across 217 plans (FY2001-2021).
Done so far: 168 rows / 8 plans (4.2% of rows, 3.7% of plans).

| Batch | Date | Plans covered | Rows added | Notes |
|---|---|---|---|---|
| pilot-batch-1-sonnet | 2026-09-22 | 8 largest plans by AUM: California PERF (9), California Teachers (10), Florida RS (26), NY State Teachers (78), NY State & Local ERS (83), Ohio PERS (85), Texas Teachers (108), Wisconsin RS (125) | 168 (21 years x 8 plans) | Single-model pass (Sonnet) only -- composition/benchmark-identity data, no annual realized-return figures yet. Sourced entirely from the Dropbox CAFR/AV/IPS archive (web access is blocked in this environment). Confidence distribution: 81 High, 68 Medium, 19 Low. Not yet cross-model-verified or deterministically quote-checked against source documents -- see docs/methodology.md's Verification section. Two plans' archives contained misfiled documents (a TRS-Texas IPS mislabeled as Wisconsin's, and a TMRS IPS mislabeled as TRS-Texas's); the research agents caught both and excluded them rather than using them. |
| user-verified-correction | 2026-09-22 | California PERF (9), FY2019 only | 3 (FY2019-2021 period corrected; FY2019 row was the actual fix) | User spot-checked FY2019 against the real CAFR (page 101) and found the pilot batch had assigned the wrong fiscal year to a correctly-extracted benchmark table (an IPS effective Sept 2019 was misattributed to start FY2020, when the plan's own CAFR shows that structure was already the disclosed "current benchmark" during FY2019). Corrected using the CAFR's own table plus the matching IPS; also added the FY2019 annual-return figures (actual vs. benchmark) as the first entries in that new schema column. See docs/agent_playbook.md's "known failure mode" section, added as a result. |
| schema restructure | 2026-09-22 | All 168 rows (schema-only change, no content change) | 0 | Replaced the free-text `asset_class_returns_json` blob with explicit `<class>_actual_return_pct` / `<class>_benchmark_return_pct` column pairs for all 9 asset classes, matching the composition columns 1:1. Rebuilt benchmarks_collected.csv from the raw pass files under this schema. |

## Systematic check for the "wrong fiscal year" failure mode

`scripts/verify_batch.py` checks every row against a real Dropbox folder
listing (`data/dropbox_index/<batch>_index.csv`, built from an actual
`mcp__Dropbox__list_folder` call -- this script cannot call Dropbox
itself): (1) does the cited source file actually exist in that plan's
folder (provenance), and (2) does the plan's folder contain an
Investment Policy Statement whose own filename year exactly matches the
row's fiscal year, that ISN'T the row's cited source (the exact bug
class that produced the CalPERS FY2019 error).

First run against the pilot batch (`data/dropbox_index/pilot_batch_1_index.csv`):
0 provenance failures, **26 same-year-IPS-not-used flags**, all on
Medium/Low-confidence rows:

- New York State Teachers (78): FY2011-2018, 8 years (every year in that
  span has its own IPS snapshot that wasn't individually used -- periods
  were built from a sparser sample and extended forward)
- Florida RS (26): FY2003, 2012, 2014, 2015, 2018 (5 years)
- Texas Teachers (108): FY2014, FY2021 (2 years)
- Ohio PERS (85): FY2009 (1 year)
- Wisconsin RS (125): FY2018 (1 year) -- note this specific file
  (`Wisconsin_InvPolStmt_2018_125.pdf.pdf`) was already found by the
  original research agent to be a *misfiled* Texas TRS document, not a
  real Wisconsin source, so this flag is a known false positive by content
  (the checker can't detect a mislabeled file's actual contents, only its
  filename's claimed year)
- California Teachers (10): FY2007, 2014, 2016 (3 years)

None of these are necessarily wrong (a benchmark set can validly persist
across a multi-year period from one IPS), but each is a case where a more
precise, same-year source exists and wasn't checked -- worth resolving
before treating those rows as final, and worth building future batches
around checking every available IPS year (they are cheap to fetch) rather
than sampling every 3-5 years.
