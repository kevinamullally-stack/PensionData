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

**If you are running with direct local filesystem access to this archive
instead of the Dropbox tools** (e.g. a synced folder on the user's own
machine), skip straight to the "Local-access mode" section below after
reading the general procedure — it overrides step 13 and the AV-fallback
guidance and removes most of the size-limit workarounds described here.

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
   and `total_fund_benchmark_return_pct` for that specific year, **and
   always also try to record the same actual/benchmark pair for every
   asset class the table breaks out** — most "Investment Results" /
   "Portfolio Comparisons" tables report actual-vs-benchmark by category
   (e.g. Public Equity, Fixed Income, Real Assets, Private Equity), not
   just at the total-fund level, so extracting only the total-fund row
   when the category-level rows are sitting right there in the same table
   is an incomplete extraction, not a genuine gap. Map each category to
   the closest field pair: `<class>_actual_return_pct` /
   `<class>_benchmark_return_pct` for `us_equity`, `intl_equity`,
   `global_equity`, `fixed_income`, `real_estate`, `private_equity`,
   `hedge_fund_absolute_return`, `real_assets_commodities`, `cash` (same
   class names as the composition fields in Part A). Use
   `other_returns_notes` for a disclosed category that doesn't map
   cleanly (e.g. a standalone "Opportunistic Funds" line). Leave a
   class's pair blank only when the table genuinely doesn't break it out.

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

13. **(Dropbox mode only) If `mcp__Dropbox__fetch` errors with
    `FILE_TOO_LARGE`** (limit is 5 MiB; many recent high-resolution CAFRs
    and old scanned volumes exceed it): try the nearest other file for
    that same fiscal year (AV instead of CAFR, or vice versa), then the
    nearest adjacent fiscal year's CAFR/AV/IPS instead. Do not skip a year
    silently — if nothing fetchable exists nearby for a policy period,
    record the gap with `confidence: Low` and say so in `notes`; for
    annual returns, just omit the year (see step 10). **This step does not
    apply in local-access mode — see that section below.**

## Local-access mode (direct filesystem access instead of Dropbox)

Use this mode instead of the Dropbox-tool steps above when the CAFR
archive is mounted as a local folder (e.g. a synced Dropbox folder on the
user's own machine) and you're reading files with the `Read` tool rather
than `mcp__Dropbox__*`. This removes the two constraints that drove most
of the cost and most of the coverage gaps in the remote/Dropbox pilot:

- **No 5 MiB fetch limit.** Step 13 above (hunting for a smaller
  substitute document, reconstructing figures from scrambled retrospective
  charts, cross-validating ambiguous digit sequences across 3-4
  documents) is a workaround for a limit that doesn't exist here — skip
  it entirely. Every CAFR in the archive is readable regardless of size.
  `Read` pages large PDFs in chunks of up to 20 pages via its `pages`
  parameter rather than refusing them outright, so a large file is a
  reason to target a page range, not a reason to abandon the document.
  Use the CAFR's own table of contents (typically in its first 5-10
  pages) to locate the Investment Section's page range before reading it;
  if there's no usable table of contents, the Investment Section is
  typically 40-70% of the way through the document — read a bracketing
  range, then narrow.

- **Don't parse Actuarial Valuation (AV) files as a routine source.** AVs
  were only ever a fallback for fiscal years whose CAFR exceeded the
  fetch limit, and even then they supplied nothing but a bare total-fund
  actual return — no benchmark, no asset-class breakdown — which is why
  every AV-sourced row in the pilot came back `confidence: Medium`. With
  unrestricted CAFR access there is essentially never a reason to open
  one. Only read a plan's AV when its folder has **no CAFR at all** for a
  given fiscal year (a genuine document gap, not a size problem) — and
  even then, prefer the CAFR's own GASB-67 "Schedule of Investment
  Returns" (Financial Section RSI, now fully readable) over a standalone
  AV/GASB67 supplement for returns data.

- **IPS files are unaffected either way** — they were never blocked by
  the size limit and remain the first source to check per step 2.

Everything else in this playbook (fiscal-year mapping rules, the
sourcing/verification requirements, both known-failure-mode sections
below, and the output format) applies unchanged in local-access mode.

## A known failure mode: matching a document to the wrong fiscal year

A pilot-batch review caught this exact bug, so check for it explicitly:
an agent found the correct IPS document (e.g. an IPS dated/named for 2019)
and correctly extracted its benchmark table, but assigned that table to
the *wrong* fiscal year (attributing it to FY2020-2021 based on the
document's formal "Effective Date," while the plan's own CAFR showed that
exact benchmark structure was already the disclosed "current benchmark"
during FY2019 itself — operational implementation had preceded the
document's formal adoption date).

To avoid this: don't assign a policy period's start year purely from an
IPS's stated "Effective Date." Cross-check against the nearest CAFR you
can fetch (or, if it's over the size limit, against a same-year IPS
snapshot if one exists) for what benchmark it says was *actually in use*
that fiscal year — a CAFR's own performance table is the better authority
on which benchmark governed a given fiscal year's results, even if a
separate IPS document's formal effective date suggests otherwise. When a
same-or-adjacent-fiscal-year IPS snapshot exists in the folder, prefer it
over an older one for that year's record, even if its stated effective
date falls a few months after the fiscal year start.

## A second pattern: a document's filename year is not its effective year

A systematic re-check of 26 candidate gaps across 6 plans (all flagged
because an IPS file's filename year matched a fiscal year that cited a
different document) found that **every one was already correct** — the
apparent gap was an artifact of a consistent dating pattern, not a real
miss:

- IPS documents are usually named/dated by their **adoption** month
  (e.g. "October 2011," "InvPolStmt_2014"), but a benchmark change
  typically doesn't take effect until a specific date stated inside the
  document — often the start of the *next* fiscal year. A plan with a
  June 30 fiscal year-end whose IPS says "effective July 1" or was
  "adopted at the July Board meeting" is describing the fiscal year
  *after* the one implied by the filename.
- Do not assign a policy period's start year from an IPS's filename or
  even its adoption date alone. Find the actual "effective [date]" or
  "adopted ... to be effective ..." language inside the document, convert
  that date to the plan's own fiscal year (which may not be a calendar
  year — check the plan's stated FYE), and use that.
- Some `InvPolStmt`-named files are not Total Fund benchmark policies at
  all (one was a narrow "in-state investments" mandate unrelated to
  asset-allocation benchmarks) — skim a document's actual subject before
  assuming its filename pattern means it's useful here.
- Some plans' older IPS scans have no OCR text layer (fetch returns
  blank/whitespace) — if a fetch returns empty text for a file, that's a
  genuine dead end, not a bug in your search; fall back to the next
  candidate source rather than retrying the same file.

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
      "us_equity_actual_return_pct": 3.8,
      "us_equity_benchmark_return_pct": 3.8,
      "intl_equity_actual_return_pct": "",
      "intl_equity_benchmark_return_pct": "",
      "global_equity_actual_return_pct": "",
      "global_equity_benchmark_return_pct": "",
      "fixed_income_actual_return_pct": 6.9,
      "fixed_income_benchmark_return_pct": 7.5,
      "real_estate_actual_return_pct": "",
      "real_estate_benchmark_return_pct": "",
      "private_equity_actual_return_pct": "",
      "private_equity_benchmark_return_pct": "",
      "hedge_fund_absolute_return_actual_return_pct": "",
      "hedge_fund_absolute_return_benchmark_return_pct": "",
      "real_assets_commodities_actual_return_pct": "",
      "real_assets_commodities_benchmark_return_pct": "",
      "cash_actual_return_pct": "",
      "cash_benchmark_return_pct": "",
      "other_returns_notes": "",
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
