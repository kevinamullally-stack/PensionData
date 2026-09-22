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
| `confidence` | `High` (primary source, explicit benchmark table), `Medium` (primary source, benchmark inferred/described narratively), `Low` (secondary source only, or partial/ambiguous evidence). |
| `researcher` | Identifier for the agent/batch that produced this record. |
| `research_date` | ISO date the record was produced. |
| `notes` | Any other caveats (e.g. benchmark changed mid-year, plan restructured, data unavailable for this specific year). |

Rows in `data/worklist.csv` without a corresponding row here are still
`pending`. A plan-year can also resolve to an explicit "not found" record
(all benchmark fields blank, `notes` explaining what was searched and why
nothing was found) rather than being left out silently.
