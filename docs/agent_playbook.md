# Research playbook for benchmark-collection agents

You are researching **one public pension plan** at a time, with two
distinct outputs:

1. **Policy periods** — which benchmark(s) the plan uses/used, at the
   total-fund and asset-class level. This changes infrequently (every few
   years), so you report it as date ranges, not one row per year.
2. **Annual returns** — the actual realized return of the total fund vs.
   its benchmark, **for each individual fiscal year**. Unlike composition,
   this is a genuinely different number every year even when the benchmark
   itself hasn't changed, so it cannot be inherited across a period — it
   must be sourced per fiscal year (though one source document, like a
   10-year historical schedule, can supply many years at once).

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

### Part A: policy periods (composition)

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

4. **Record the total-fund policy benchmark** exactly as described — it is
   very often a *composite/custom* index defined as a weighted blend of
   asset-class benchmarks per target allocation. Record the literal
   weights/index names given, not a paraphrase.

5. **Record each asset-class benchmark** mentioned, mapped to the closest
   category in `data/schema.md` (US equity, international equity, fixed
   income, real estate, private equity, hedge fund/absolute return, real
   assets/commodities, cash). Skip fields the plan's documents don't cover.

6. **Bracket each policy period** using explicit effective dates when the
   source gives them (most precise); otherwise infer a boundary from which
   fiscal years' CAFRs show the old vs. new benchmark, and mark
   `confidence: Medium` for an inferred boundary.

### Part B: annual returns (per fiscal year)

7. **Look for a historical returns schedule.** Search recent CAFRs first —
   the Investment Section or the Statistical Section usually has a table
   titled something like "Schedule of Investment Results," "Comparative
   Investment Results," "Time-Weighted Rates of Return," or "Investment
   Summary," typically showing 5-10 fiscal years side by side (Total Fund
   Actual Return vs. Total Fund Benchmark/Policy Return per year). One
   recent CAFR can often cover most of your assigned range this way —
   check the most recent few CAFRs first, then reach for older ones only to
   fill years the recent schedules don't cover.

8. **Record one entry per fiscal year**: `total_fund_actual_return_pct`
   and `total_fund_benchmark_return_pct` for that specific year, plus any
   per-asset-class actual/benchmark pairs the same table discloses (put
   those in `asset_class_returns_json`, e.g.
   `{"us_equity": {"actual": 8.2, "benchmark": 7.9}}` — omit if the table
   is total-fund-only).

9. **Do not confuse trailing/annualized figures with single-year returns.**
   A table column labeled "5-Year" or "10-Year" is an annualized return
   over that trailing window, not the single fiscal year's return — only
   record it under `total_fund_actual_return_pct`/`..._benchmark_return_pct`
   if it is clearly the 1-year figure for that specific fiscal year.

10. **If a fiscal year has no returns table available anywhere in the
    archive**, don't fabricate one — omit that year from `annual_returns`
    rather than guessing.

### Sourcing and verification for both parts

11. **Always cite your source** for every policy-period and every
    annual-return entry: `source_type`/`returns_source_type` (`IPS`,
    `CAFR`, or `AV`), the exact filename, and the fiscal year that document
    itself covers. Use the Dropbox path as the URL, e.g.
    `/Kevin/RevolvingDoor/CAFR2024/88_Ohio Teachers/OhioTRS_InvPolStmt_2012_88.pdf.pdf`.

12. **Include a verbatim quote and page number for every entry.** Copy the
    exact sentence or table fragment (not the whole page) from the fetched
    text that states what you recorded — this is what gets checked against
    the real document during verification, so it must be a real substring
    of the extracted text, not a paraphrase. The Dropbox text extraction
    preserves page-number footers as a lone number on its own line between
    blocks of blank lines (e.g. `\n\n\n\n9 \n\nInvestment...`) — find the
    nearest such number appearing just before your quote and report it as
    the page. Leave the page field blank if the document has no such
    markers (e.g. an old scanned volume with no embedded text layer).

13. **If `mcp__Dropbox__fetch` errors with `FILE_TOO_LARGE`** (limit is
    5 MiB; many recent high-resolution CAFRs and old scanned volumes exceed
    it): try the nearest other file for that same fiscal year (AV instead
    of CAFR, or vice versa), then the nearest adjacent fiscal year's
    CAFR/AV/IPS instead. Do not skip a year silently — if nothing fetchable
    exists nearby for a policy period, record the gap with `confidence:
    Low` and say so in `notes`; for annual returns, just omit the year (see
    step 10).

## What NOT to do

- Do not infer a benchmark or a return figure from what a "typical" plan of
  that type uses. Every record must trace to something you actually read
  for that plan.
- Do not attempt WebSearch/WebFetch as a primary source — it is blocked in
  this environment and will waste time. The Dropbox archive has 100% plan
  coverage; if a specific year is genuinely missing from it, say so rather
  than substituting a web guess.
- Do not assume the benchmark never changed across the full range just
  because you only checked one document — check enough spread-out
  years/documents to catch a revision (step 3).
- Do not report a trailing/annualized multi-year return as if it were a
  single fiscal year's return (step 9).

## Output format

Return a single JSON object with two arrays, `policy_periods` and
`annual_returns`. Nothing else before or after it.

```json
{
  "policy_periods": [
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
      "source_page": 14,
      "source_quote": "Effective July 1, 2012 the Total Fund benchmark will be calculated using 18% Barclays Capital Universal Index, 38% Russell 3000, 23% International Blended Benchmark, 10% Real Estate Blended Benchmark, 10% Alternative Investment actual return, and 1% 3-month Treasury Bill Index.",
      "confidence": "High",
      "notes": "IPS also defines a second period effective 1/1/2013 with revised weights -- see separate period object."
    }
  ],
  "annual_returns": [
    {
      "ppd_id": 88,
      "plan_name": "Ohio Teachers",
      "fy": 2012,
      "total_fund_actual_return_pct": 1.4,
      "total_fund_benchmark_return_pct": 1.1,
      "asset_class_returns_json": "{\"us_equity\": {\"actual\": 3.8, \"benchmark\": 3.8}}",
      "returns_source_type": "CAFR",
      "returns_source_document_name": "OH-OH-STRS_CAFR_2016_88.pdf.pdf",
      "returns_source_url": "/Kevin/RevolvingDoor/CAFR2024/88_Ohio Teachers/OH-OH-STRS_CAFR_2016_88.pdf.pdf",
      "returns_source_document_fy": 2016,
      "returns_source_page": 62,
      "returns_source_quote": "Fiscal Year 2012 ... Total Fund 1.4% ... Benchmark 1.1%",
      "returns_confidence": "High",
      "notes": "From the FY2016 CAFR's 10-year comparative schedule, which retrospectively reports FY2012."
    }
  ]
}
```

List every policy period and every annual-return year you can document for
the plan's full assigned fiscal-year range. The pipeline expands each
policy period to every fiscal year in the worklist automatically; annual
returns are merged in directly by fiscal year.
