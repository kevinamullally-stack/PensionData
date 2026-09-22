# Research playbook for benchmark-collection agents

You are researching **one public pension plan** at a time. Your job: find
the investment-return benchmark(s) it used to evaluate performance, for
every fiscal year assigned to you, using the policy-period method below.

**Web access is blocked in this environment.** Do not use WebFetch/WebSearch
for primary sourcing — it will fail. Your source is a Dropbox archive of
each plan's own CAFRs, Actuarial Valuations, and Investment Policy
Statements, accessed via the `mcp__Dropbox__*` tools.

## Procedure

1. **List the plan's folder**: `mcp__Dropbox__list_folder` on
   `/Kevin/RevolvingDoor/CAFR2024/<ppd_id>_<PlanName>` (exact folder name
   given in your assignment). Files are named
   `<STATE>_<PLANCODE>_<DOCTYPE>_<year(s)>_<ppd_id>.pdf.pdf` where DOCTYPE is
   `CAFR`, `AV` (Actuarial Valuation), or a plan-specific Investment Policy
   Statement name (e.g. `OhioTRS_InvPolStmt_2012_88.pdf.pdf`). Some year
   values are ranges (e.g. `1937-1942`) for old combined volumes.

2. **Fetch Investment Policy Statement files first** — these are the single
   best source and are usually small. Use `mcp__Dropbox__fetch` with the
   file's path. IPS documents typically state the total-fund benchmark
   formula explicitly, often with **effective dates for each revision**
   (e.g. "Effective July 1, 2012 the Total Fund benchmark will be calculated
   using 18% Barclays Capital Universal Index, 38% Russell 3000, 23%
   International Blended Benchmark, 10% Real Estate Blended Benchmark, 10%
   Alternative Investment actual return, and 1% 3-month Treasury Bill Index.
   Effective January 1, 2013 the Total Fund benchmark will be calculated
   using ..." — that single document can define two policy periods by
   itself). Read for asset-class sub-benchmarks too (international,
   real estate, fixed income sections typically define their own blended
   benchmark).

3. **Fill gaps with CAFR/AV files spread across your fiscal-year range**
   (e.g. ~every 3-5 years) via `mcp__Dropbox__fetch`. CAFR Investment
   Sections usually have a "Policy Index," "Total Fund Benchmark," or
   "Investment Results vs. Benchmark" table for that fiscal year — use it to
   confirm or extend a policy period found from an IPS, or as your only
   source when no IPS snapshot exists nearby.

4. **If `mcp__Dropbox__fetch` errors with `FILE_TOO_LARGE`** (limit is 5 MiB;
   many recent high-resolution CAFRs and old scanned volumes exceed it):
   try the nearest other file for that same fiscal year (AV instead of
   CAFR, or vice versa), then the nearest adjacent fiscal year's CAFR/AV/IPS
   instead. Do not skip the year silently — if nothing fetchable exists
   nearby, record it as a gap with `confidence: Low` and say so in `notes`.

5. **Record the total-fund policy benchmark** exactly as described — it is
   very often a *composite/custom* index defined as a weighted blend of
   asset-class benchmarks per target allocation. Record the literal
   weights/index names given, not a paraphrase.

6. **Record each asset-class benchmark** mentioned, mapped to the closest
   category in `data/schema.md` (US equity, international equity, fixed
   income, real estate, private equity, hedge fund/absolute return, real
   assets/commodities, cash). Skip fields the plan's documents don't cover.

7. **Bracket each policy period** using explicit effective dates when the
   source gives them (most precise); otherwise infer a boundary from which
   fiscal years' CAFRs show the old vs. new benchmark, and mark
   `confidence: Medium` for an inferred boundary.

8. **Always cite your source**: `source_type` (`IPS`, `CAFR`, or `AV`),
   `source_document_name` (the exact filename), and `source_document_fy`.
   `source_url` should be the Dropbox path (e.g.
   `/Kevin/RevolvingDoor/CAFR2024/88_Ohio Teachers/OhioTRS_InvPolStmt_2012_88.pdf.pdf`).

## What NOT to do

- Do not infer a benchmark from what a "typical" plan of that type uses.
  Every record must trace to something you actually read for that plan.
- Do not attempt WebSearch/WebFetch as a primary source — it is blocked in
  this environment and will waste time. The Dropbox archive has 100% plan
  coverage; if a specific year is genuinely missing from it, say so rather
  than substituting a web guess.
- Do not assume the benchmark never changed across the full range just
  because you only checked one document — check enough spread-out
  years/documents to catch a revision (step 3).

## Output format

Return one JSON object per **policy period** you find (not per fiscal
year), shaped like:

```json
{
  "ppd_id": 88,
  "plan_name": "Ohio Teachers",
  "policy_period_start": 2012,
  "policy_period_end": 2012,
  "total_fund_benchmark": "18% Barclays Capital Universal Index, 38% Russell 3000, 23% International Blended Benchmark, 10% Real Estate Blended Benchmark, 10% Alternative Investment actual return, 1% 3-month Treasury Bill Index (effective 7/1/2012)",
  "us_equity_benchmark": "Russell 3000",
  "intl_equity_benchmark": "80% MSCI World ex-US (50% hedged), 20% MSCI Emerging Markets Free Index",
  "global_equity_benchmark": "",
  "fixed_income_benchmark": "Barclays Capital Universal Index",
  "real_estate_benchmark": "85% NCREIF Property Index, 15% Wilshire REIT Index (through 6/30/2012)",
  "private_equity_benchmark": "",
  "hedge_fund_absolute_return_benchmark": "Alternative Investment actual return (no external benchmark)",
  "real_assets_commodities_benchmark": "",
  "cash_benchmark": "91-day T-Bill",
  "other_asset_classes_notes": "",
  "source_type": "IPS",
  "source_document_name": "OhioTRS_InvPolStmt_2012_88.pdf.pdf",
  "source_url": "/Kevin/RevolvingDoor/CAFR2024/88_Ohio Teachers/OhioTRS_InvPolStmt_2012_88.pdf.pdf",
  "source_document_fy": 2012,
  "confidence": "High",
  "notes": "IPS also defines a second period effective 1/1/2013 with revised weights -- see separate period object."
}
```

List every policy period you identify for the plan, covering the plan's
full assigned fiscal-year range. Report periods only — the pipeline expands
each period to every fiscal year in the worklist automatically.
