# Research playbook for benchmark-collection agents

You are researching **one public pension plan** at a time. Your job: find
the investment-return benchmark(s) it used to evaluate performance, for
every fiscal year assigned to you, using the policy-period method below.

## Procedure

1. **Find the plan's CAFR/ACFR archive.** Search `"<plan full name>" annual
   comprehensive financial report` or `"<plan full name>" CAFR filetype:pdf`.
   Most plans host an archive of past CAFRs/ACFRs on their own website
   (often under "Financial Reports" or "Publications"). Prefer the plan's
   own domain over aggregators.
2. **Open the Investment Section of 2-4 CAFRs spread across your assigned
   fiscal-year range** (e.g. for 2001-2021, check something like FY2003,
   FY2009, FY2015, FY2021) — enough to detect when the benchmark set
   changed. Look for tables titled "Target Asset Allocation," "Investment
   Results," "Policy Index," "Performance vs. Benchmark," or similar.
3. **Record the total-fund policy benchmark** exactly as described (it is
   very often a *composite/custom* index defined as "weighted average of
   asset-class benchmarks per target allocation" rather than a single named
   index — record it that way if that's what the source says).
4. **Record each asset-class benchmark** named in that table, mapped to the
   closest category in `data/schema.md` (US equity, international equity,
   fixed income, real estate, private equity, hedge fund/absolute return,
   real assets/commodities, cash). If the plan doesn't have a category, skip
   that field.
5. **Bracket the policy period**: once you find a benchmark set in FY_X and
   it differs from the previous one you found, narrow down (or reasonably
   infer from context — e.g. IPS revision dates mentioned in board minutes)
   the fiscal year the change took effect. It is fine to state an
   approximate boundary with `confidence: Medium` if the exact transition
   year isn't pinned down.
6. **If a plan's IPS/CAFR is not findable** for part of the range, say so
   explicitly rather than guessing — leave those years as a `notes`-only
   record with blank benchmark fields and `confidence: Low`.
7. **Always cite your source**: `source_type`, `source_document_name`,
   `source_url`, and `source_document_fy`.

## What NOT to do

- Do not infer a benchmark from what a "typical" plan of that type uses.
  Every record must trace to something you actually read for that plan.
- Do not treat a secondary aggregator (NASRA summaries, Wikipedia, generic
  finance blogs) as sufficient sourcing on its own — use it only to locate
  the primary document, and mark `confidence: Low` if a primary source
  genuinely can't be found.
- Do not assume the benchmark never changed across 21 years just because
  you only checked one year — check enough spread-out years to catch a
  revision (see step 2).

## Output format

Return one JSON object per **policy period** you find (not per fiscal
year), shaped like:

```json
{
  "ppd_id": 9,
  "plan_name": "California PERF",
  "policy_period_start": 2011,
  "policy_period_end": 2015,
  "total_fund_benchmark": "Custom Policy Index weighted per target asset allocation",
  "us_equity_benchmark": "Russell 3000",
  "intl_equity_benchmark": "MSCI ACWI ex-US IMI",
  "global_equity_benchmark": "",
  "fixed_income_benchmark": "Bloomberg Barclays US Aggregate",
  "real_estate_benchmark": "NCREIF ODCE (net)",
  "private_equity_benchmark": "Russell 3000 + 300bps (custom)",
  "hedge_fund_absolute_return_benchmark": "",
  "real_assets_commodities_benchmark": "CPI + 4%",
  "cash_benchmark": "91-day T-Bill",
  "other_asset_classes_notes": "",
  "source_type": "CAFR",
  "source_document_name": "CalPERS FY2013 CAFR, Investment Section p.XX",
  "source_url": "https://...",
  "source_document_fy": 2013,
  "confidence": "High",
  "notes": ""
}
```

List every policy period you identify for the plan, covering the plan's
full assigned fiscal-year range. Report periods only — the pipeline expands
each period to every fiscal year in the worklist automatically.
