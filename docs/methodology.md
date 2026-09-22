# Methodology: Collecting Investment-Return Benchmark Data

## Why this exists

The [Public Plans Database (PPD)](https://publicplansdata.org/) — the source
panel in `data/source/ppd_plan_level_clean.dta` — covers 217 U.S. public
pension plans across fiscal years 2001-2021 (~4,000 plan-year rows). It
records actuarial assumptions, funded ratios, and realized investment
returns, but **not** the benchmark indices each plan uses to judge whether
those returns were good. That is the gap this project fills in.

"The benchmark" a plan uses for performance evaluation is really two things:

1. **A total fund policy benchmark** — a blended, weighted composite of
   asset-class benchmarks matching the plan's target asset allocation. Some
   plans name it explicitly ("Policy Index"); others only describe it as
   "a custom weighted index based on target allocation."
2. **Asset-class benchmarks** — the individual index assigned to each asset
   class in the plan's investment policy (e.g. Russell 3000 for U.S. equity,
   Bloomberg U.S. Aggregate for core fixed income, NCREIF ODCE for real
   estate).

## The policy-period approach (why we don't do 4,000 independent lookups)

Plans revise their Investment Policy Statement (IPS) and benchmark set
episodically — typically every 3-7 years — not annually. Researching each of
the ~21 fiscal years per plan independently would be redundant and would
multiply cost with no gain in accuracy.

Instead, for each plan, research agents:

1. Identify each **policy period**: a contiguous range of fiscal years
   during which the plan's total-fund and asset-class benchmarks stayed the
   same, as disclosed in that plan's own primary sources.
2. Record the benchmark set **once per policy period**, with the source
   document that supports it.
3. The period is then mechanically expanded to every fiscal year in
   `data/worklist.csv` that falls inside it — this is what
   `scripts/merge_policy_periods.py` does.

A plan with one IPS revision over 2001-2021 might need only 2 real lookups
to cover all 21 worklist rows; a plan that revised its benchmarks four times
needs ~5. This is both more efficient and more accurate than assuming
year-over-year continuity without evidence.

## Sourcing standards

Preferred sources, in order:

1. **The plan's own CAFR / ACFR** (Annual Comprehensive Financial Report),
   Investment Section — almost always includes a "Target Asset Allocation"
   table and a "Performance vs. Benchmark" or "Policy Index" table for that
   fiscal year.
2. **The plan's Investment Policy Statement (IPS)**, published on the plan's
   own website or board-meeting agenda packet — states benchmarks
   prospectively and the effective date of any revision.
3. **Investment consultant reports** (Callan, Wilshire, Aon, Meketa, RVK,
   NEPC, etc.) presented at public board meetings — often the most detailed
   asset-class-level source, and usually posted as public board materials.
4. **NASRA / secondary aggregators** — acceptable only to corroborate or
   locate primary sources, never as the sole source; mark `confidence` as
   `Low` if a record rests only on a secondary source.

Every record must carry: `source_type`, `source_document_name`,
`source_url` (or citation if no stable URL exists), the fiscal year(s) the
source document itself covers, and a `confidence` rating. See
`docs/agent_playbook.md` for the exact research procedure given to agents,
and `data/schema.md` for the output column definitions.

## Status tracking

`data/worklist.csv` has a `status` column (`pending` / `in_progress` /
`done`) and a `batch` column identifying which research batch covered each
row. `data/benchmarks_collected.csv` accumulates one row per plan-year as
batches complete. `docs/progress.md` logs each batch: which plans, how many
rows, and any data-quality caveats.
