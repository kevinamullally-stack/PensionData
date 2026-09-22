# `data/benchmarks_collected.csv` — column dictionary

| Column | Description |
|---|---|
| `ppd_id` | Plan identifier, matches `ppd_id` in the PPD source file and `data/worklist.csv`. |
| `PlanName` | Short plan name, as in PPD. |
| `StateAbbrev` | Two-letter state postal abbreviation. |
| `fy` | Fiscal year (matches PPD `fy`). |
| `policy_period_start` / `policy_period_end` | Fiscal-year range, per the source document, during which this benchmark set was in effect. May extend beyond the worklist's 2001-2021 window. |
| `total_fund_benchmark` | Name/description of the blended total-fund policy benchmark (e.g. "Custom Policy Index weighted per target asset allocation", or a named index if the plan uses one directly). |
| `us_equity_benchmark` | Benchmark assigned to U.S./domestic equity (e.g. Russell 3000, S&P 500, Dow Jones U.S. Total Stock Market). |
| `intl_equity_benchmark` | Benchmark for non-U.S./international equity (e.g. MSCI ACWI ex-US IMI, MSCI EAFE). |
| `global_equity_benchmark` | Benchmark for a combined global equity sleeve, if the plan does not split U.S./international (e.g. MSCI ACWI). |
| `fixed_income_benchmark` | Benchmark for core/core-plus fixed income (e.g. Bloomberg U.S. Aggregate, formerly Barclays/Lehman Aggregate). |
| `real_estate_benchmark` | Benchmark for real estate (e.g. NCREIF ODCE, NCREIF Property Index). |
| `private_equity_benchmark` | Benchmark for private equity / private markets (e.g. Russell 3000 + premium, Cambridge Associates PE Index). |
| `hedge_fund_absolute_return_benchmark` | Benchmark for hedge funds / absolute return / diversifying strategies (e.g. HFRI FoF Index, CPI + spread). |
| `real_assets_commodities_benchmark` | Benchmark for real assets, infrastructure, or commodities (e.g. Bloomberg Commodity Index, CPI + spread). |
| `cash_benchmark` | Benchmark for cash/short-term (e.g. 91-day T-Bill, ICE BofA 3-Month T-Bill). |
| `other_asset_classes_notes` | Free text for any additional asset classes / benchmarks not covered above. |
| `source_type` | One of: `CAFR`, `ACFR`, `IPS`, `Consultant Report`, `Board Minutes`, `Other`. |
| `source_document_name` | Title/identifier of the source document. |
| `source_url` | URL to the source document (or citation, if no stable URL). |
| `source_document_fy` | Fiscal year(s) the cited source document itself covers (may differ slightly from `fy`). |
| `source_page` | Page number within the source document where the cited language appears, when determinable from the extracted text (the Dropbox text extraction preserves page-number footers). Blank if the document is a scanned image with no embedded page markers. |
| `source_quote` | A short verbatim excerpt (one sentence or table fragment, not the whole page) from the source document that states the benchmark(s) recorded in this row. This is what verification checks against the actual re-fetched document. |
| `confidence` | `High` (primary source, explicit benchmark table), `Medium` (primary source, benchmark inferred/described narratively), `Low` (secondary source only, or partial/ambiguous evidence). |
| `total_fund_actual_return_pct` | The plan's own realized total-fund return for this specific fiscal year, as reported alongside the benchmark comparison in the source (cross-check against PPD's own `InvestmentReturn_1yr` for this plan-year; a mismatch is worth a note, not a silent overwrite). |
| `total_fund_benchmark_return_pct` | The total-fund policy benchmark's realized return for this specific fiscal year, as reported in the same table. This is a per-fiscal-year figure — unlike the composition fields above, it cannot be inherited across a policy period and must be sourced per year. |
| `<class>_actual_return_pct` / `<class>_benchmark_return_pct` | One pair per asset class (`us_equity`, `intl_equity`, `global_equity`, `fixed_income`, `real_estate`, `private_equity`, `hedge_fund_absolute_return`, `real_assets_commodities`, `cash`) — the realized actual and benchmark return for that class, for this specific fiscal year, whenever the source's performance table discloses it (most "Investment Results"/"Portfolio Comparisons" tables report actual-vs-benchmark by category, not just at the total-fund level — always attempt these, not just the total-fund figure). Blank if that class isn't broken out or isn't disclosed for this year. |
| `other_returns_notes` | Free text for any additional category's actual-vs-benchmark return the source discloses that doesn't map to one of the classes above (e.g. an "Opportunistic Funds" line). |
| `returns_source_type` / `returns_source_document_name` / `returns_source_url` / `returns_source_document_fy` / `returns_source_page` / `returns_source_quote` | Separate provenance for the returns figures, mirroring the `source_*` fields above — the returns table is often in a different document/page than the benchmark composition (e.g. a 10-year "Schedule of Investment Results" in a later CAFR's Statistical Section covering this fiscal year retrospectively). |
| `returns_confidence` | Same scale as `confidence`, rated independently for the returns figures. |
| `cross_model_agreement` | `agree` (two independent model passes matched), `disagree` (they didn't — see `notes` for both readings), or `single-pass-only` (only one model pass was run for this record). A `disagree` record needs manual review before being treated as final. |
| `researcher` | Identifier for the agent/batch/model that produced this record (e.g. `pilot-batch-1-sonnet`, `pilot-batch-1-opus`). |
| `research_date` | ISO date the record was produced. |
| `notes` | Any other caveats (e.g. benchmark changed mid-year, plan restructured, data unavailable for this specific year, or both readings from a `disagree` cross-model check). |

Rows in `data/worklist.csv` without a corresponding row here are still
`pending`. A plan-year can also resolve to an explicit "not found" record
(all benchmark fields blank, `notes` explaining what was searched and why
nothing was found) rather than being left out silently.
