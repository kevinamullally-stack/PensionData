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

### Resolution: all 26 flags investigated, 0 corrections needed

Fetched every candidate same-year IPS (except the 2 already-known
misfiled documents) and checked each one's actual stated effective date
against the plan's real fiscal-year-end. Result:

- **12 false positives**: CalSTRS FY2007/2016, Ohio PERS FY2009, Texas
  Teachers FY2014, NYSTRS FY2011-2018. In every case the IPS's filename
  year reflects its *adoption* date, but its benchmark table doesn't take
  effect until the start of the *next* fiscal year -- the original
  research had already assigned it there correctly. See
  docs/agent_playbook.md's new "filename year is not effective year"
  section.
- **1 not-a-benchmark-document**: CalSTRS FY2014's flagged file is a
  narrow "Policy on California Investments" mandate, unrelated to
  Total Fund asset-allocation benchmarks.
- **2 already-known misfiled documents**: Texas Teachers FY2021,
  Wisconsin RS FY2018 (both previously identified as belonging to a
  different plan).
- **1 more false positive**: Florida RS FY2018 (effective FY2019, matches
  original).
- **10 confirmed-unfixable gaps**: Florida RS FY2003, 2007, 2008,
  2010-2015, 2017 -- every flagged Florida IPS re-fetched and confirmed to
  return blank/whitespace text (scanned images, no OCR layer). The
  original SBA Annual Investment Report-based sourcing for these years
  remains the best available.

All 26 rows annotated with a `REVIEWED` note explaining the resolution;
`scripts/verify_batch.py` now skips rows already marked `REVIEWED` so
re-runs stay focused on genuinely new findings.

## Annual realized-returns pass (returns-pass-1)

Ran a second wave of 8 research agents (one per pilot plan), narrower in
scope than the original composition pass: collect actual vs. benchmark
realized returns per fiscal year, at both total-fund and asset-class
level, using the same Dropbox CAFR/AV/AIR archive. The 5MB Dropbox fetch
limit bites harder here than in the composition pass, since a plan's most
recent (largest, most information-rich) CAFRs are often the ones that
exceed it -- so coverage is real but incomplete for several plans. Where a
native fiscal-year source wasn't fetchable, agents used retrospective
multi-year schedules (20-year summary tables, GASB-67 money-weighted
return schedules) embedded in smaller documents, clearly flagged
Medium-confidence and noted as a different return-calculation methodology
(money-weighted/net vs. time-weighted) where applicable. No figures were
fabricated; genuine gaps were left blank.

Final coverage (all 8 agents complete; rows with
`total_fund_actual_return_pct` populated): 147 of 168 plan-years (87.5%).

| Plan | Years covered | Gaps |
|---|---|---|
| NY State & Local ERS (83) | 21 / 21 | none |
| New York State Teachers (78) | 21 / 21 | none |
| Texas Teachers (108) | 21 / 21 | none |
| Florida RS (26) | 20 / 21 | FY2013 (no fetchable source of any kind) |
| California PERF (9) | 17 / 21 | FY2014, 2017, 2020, 2021 (CAFRs too large, no substitute found) |
| California Teachers / CalSTRS (10) | 17 / 21 | FY2018-2021 (CAFRs too large, no AV disclosure) |
| Ohio PERS (85) | 16 / 21 | FY2001-2003, 2005-2006 (CAFRs too large, no AV exists pre-2008) |
| Wisconsin RS (125) | 14 / 21 | FY2001, 2004-2005, 2018-2021 (CAFRs too large; WRS's Investment Section is mostly narrative with no per-year table outside the FY2017 CAFR) |

Every populated row carries a verbatim source quote, page, document name,
and a `returns_confidence` rating; multi-year trailing columns (3/5/10-yr)
were explicitly excluded, only genuine 1-year figures were recorded.
Nearly all remaining gaps share one root cause: the plan's own CAFR for
that fiscal year exceeds the Dropbox 5MB fetch limit and no smaller
substitute document (AV, AIR, retrospective schedule) discloses the
figure -- the same limitation flagged throughout the composition pass.
Resolving most of these gaps would require the user's planned local-PC
session with direct disk access to the full-size CAFRs.

## Scaling decision: remaining ~209 plans

Confirmed the Dropbox archive has a folder for all 217 worklist plans
(226 folders total; 9 extras not in scope) -- source coverage is not a
blocker for any plan. The 217 plans' AUM is heavily concentrated: the 8
pilot plans alone are 35.4% of total assets ($5.1T across the full
worklist); top 20 = 54.7%, top 50 = 77.1%, top 100 = 93.3%.

Decided (2026-09-22): target **all 217 plans**, but **hold further
collection until the user's local-access session is set up** (direct
filesystem access to the synced Dropbox folder, using
`docs/agent_playbook.md`'s new "Local-access mode" section) rather than
continuing now against the remote Dropbox tools' 5 MiB fetch limit.
Rationale: the pilot's returns pass showed the fetch limit is the
dominant driver of both token cost (retrospective-chart reconstruction
across multiple documents to work around blocked CAFRs, e.g. CalSTRS'
137 tool calls / ~320k tokens) and coverage gaps (87.5% returns
coverage, concentrated in exactly the plans/years whose CAFRs were too
large); local access is expected to substantially cut cost and close
most of those gaps, so it is worth waiting for rather than repeating the
same limitation across 209 more plans.

Next step once local access is available: run the full 217-plan
composition + returns collection in waves (~8-10 plans/wave, matching
pilot batch size), following the existing per-wave checklist --
rebuild each wave's Dropbox/local file index fresh (don't reuse a stale
one, per the Florida RS AV index gap found and fixed after the pilot),
merge via `scripts/merge_batch.py`, run `scripts/verify_batch.py`
against that fresh index, spot-check a sample, then commit/push before
starting the next wave.

### First priority for the local session: backfill the 8 pilot plans' 21 gap years

Before starting new plans, use local access to close the 21
returns-pass gaps left by the 5MB fetch limit in the 8 already-completed
plans (composition is already 100% complete for all 8; only annual
returns has gaps). `data/local_access_backfill.csv` lists every gap row
with the specific oversized CAFR that blocked it (all confirmed to
exist in Dropbox, sizes 5.7-42.1MB) -- these are recoverable, not
missing-source gaps. For each row: read the named CAFR locally (Investment
Section, per the playbook's Local-access mode page-range guidance),
extract that fiscal year's actual-vs-benchmark figures the same way as
the original pass, then merge with `scripts/merge_batch.py` using a new
batch name (e.g. `returns-pass-2-local`) so `cross_model_agreement`
reflects the new pass. Two rows (Ohio PERS FY2001-2003/2005-2006) have
no AV fallback at all before 2008, so the CAFR is the only possible
source. Wisconsin RS's later gap years may still only yield a
total-fund-only figure even with full access, since its Investment
Section is mostly narrative outside the FY2017 CAFR (see the CSV's
notes column) -- that's a genuine content limitation, not a size one.

### Attempted 2026-09-22 in a remote session: local-access mode unavailable

A session was started to run the backfill above in local-access mode,
pointed at the synced Dropbox folder
`C:\Users\kevin\Dropbox\Kevin\RevolvingDoor\CAFR2024`. It could not
proceed, and no rows were collected. Recording the findings so the next
attempt doesn't repeat them:

- **The session ran in a remote Linux cloud container, not on the user's
  PC.** The Windows path does not exist there, and neither does any
  mount of it (checked `/mnt`, `/media`, and a filesystem-wide search for
  `Dropbox` and `CAFR2024` -- zero hits). Only the git repo is present.
  Local-access mode requires Claude Code running *on the machine that has
  the synced folder*; a remote session cannot reach it, so it falls back
  to the `mcp__Dropbox__*` tools and the 5 MiB limit -- exactly the
  constraint local access was meant to remove.
- **All 21 backfill rows are blocked remotely, not merely some.** Every
  blocking file is 5.7-42.1 MB. Confirmed directly: the *smallest* of
  them (`CA_CA-CALSTRS_CAFR_2020_10.pdf.pdf`, 5,733,502 bytes) returns
  `FILE_TOO_LARGE` from `mcp__Dropbox__fetch` (limit 5,242,880 bytes).
- **A promising remote workaround exists but is currently blocked by
  egress policy.** `mcp__Dropbox__download_link` does return a valid
  single-use URL for the *full* file regardless of size (verified on the
  14.2 MB `CA_CA-CALPERS_CAFR_2014_9.pdf.pdf`), which would sidestep the
  5 MiB text-extraction limit entirely -- download the PDF, parse it
  locally with `pypdf`. But the download host
  `dl.dropboxusercontent.com` is denied by the environment's egress
  policy (`connect_rejected`, 403 on CONNECT). Per the agent proxy's
  README, policy denials are to be reported, not routed around.
  **If a future remote session is wanted, allowlisting
  `*.dropboxusercontent.com` for egress would make full-size CAFR access
  work remotely and make local-access mode unnecessary.** Note `pypdf`
  needs `pip install --upgrade cffi cryptography` first in that image --
  the preinstalled Debian `cryptography` breaks its import.

Decision (unchanged): the backfill and all further collection wait for a
session running locally on the user's own machine, per the local-access
plan above.
