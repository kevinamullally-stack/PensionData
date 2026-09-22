# PensionData: Public Pension Investment-Return Benchmarks

This project collects the **investment-return benchmarks** that U.S. public
pension plans use to evaluate their own performance — both the blended
total-fund policy benchmark and the individual asset-class benchmarks
(U.S. equity, international equity, fixed income, real estate, private
equity, etc.) — and joins that data to the
[Public Plans Database (PPD)](https://publicplansdata.org/) panel of 217
plans across fiscal years 2001-2021.

The PPD itself does not include benchmark index data, so this repo builds
it via primary-source research (CAFRs/ACFRs, Investment Policy Statements,
and public consultant reports) rather than any API or scrape.

## Layout

```
data/
  source/
    ppd_plan_level_clean.dta        Raw PPD source file, as provided
    ppd_plan_level_index.csv        Trimmed identifying/context columns per plan-year
  worklist.csv                      One row per plan-year needing benchmark research + status
  benchmarks_collected.csv          Collected benchmark records (grows as batches complete)
  schema.md                         Column dictionary for benchmarks_collected.csv
docs/
  methodology.md                    Why/how: the "policy period" research approach, sourcing standards
  agent_playbook.md                 Exact procedure given to research agents
  progress.md                       Batch-by-batch log of what's been collected
scripts/
  build_worklist.py                 Regenerate worklist.csv / index.csv from the source .dta
  merge_policy_periods.py           Expand a batch's found policy periods into worklist rows
```

## Status

See `docs/progress.md` for current coverage (plans/rows completed vs. the
4,000-row worklist) and `data/worklist.csv`'s `status` column for granular,
per-plan-year tracking.

## Regenerating the worklist

```
python3 scripts/build_worklist.py data/source/ppd_plan_level_clean.dta
```

## Recording a research batch

Agents produce a JSON list of policy-period objects (see
`docs/agent_playbook.md` for the shape). Merge a batch with:

```
python3 scripts/merge_policy_periods.py path/to/batch.json <batch-name>
```

This expands each period into per-fiscal-year rows in
`data/benchmarks_collected.csv` and marks the corresponding rows in
`data/worklist.csv` as `done`.
