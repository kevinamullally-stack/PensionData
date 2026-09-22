# PensionData: Public Pension Investment-Return Benchmarks

This project collects the **investment-return benchmarks** that U.S. public
pension plans use to evaluate their own performance — the blended
total-fund policy benchmark, the individual asset-class benchmarks (U.S.
equity, international equity, fixed income, real estate, private equity,
etc.), and each fiscal year's actual realized return vs. that benchmark —
and joins that data to the
[Public Plans Database (PPD)](https://publicplansdata.org/) panel of 217
plans across fiscal years 2001-2021.

The PPD itself does not include benchmark data, so this repo builds it via
primary-source research (each plan's own CAFRs/ACFRs, Actuarial Valuations,
and Investment Policy Statements) rather than any API or scrape. Outbound
web access is blocked in this execution environment, so sourcing comes from
a Dropbox archive of those documents (see `docs/methodology.md`) instead of
live web fetching.

Every record is produced by two independent model passes per plan and
reconciled — agreement is trusted, disagreement is flagged for manual
review (`cross_model_agreement` column) — and every value carries a
verbatim quote and page number back to its source document (see
`docs/agent_playbook.md`), which is checked during verification before
anything is treated as final.

## Layout

```
data/
  source/
    ppd_plan_level_clean.dta        Raw PPD source file, as provided
    ppd_plan_level_index.csv        Trimmed identifying/context columns per plan-year
  worklist.csv                      One row per plan-year needing benchmark research + status
  benchmarks_collected.csv          Collected benchmark + returns records (grows as batches complete)
  schema.md                         Column dictionary for benchmarks_collected.csv
docs/
  methodology.md                    Why/how: policy-period approach, Dropbox sourcing, verification
  agent_playbook.md                 Exact procedure given to research agents (composition + returns)
  progress.md                       Batch-by-batch log of what's been collected
scripts/
  build_worklist.py                 Regenerate worklist.csv / index.csv from the source .dta
  merge_batch.py                    Reconcile one or two model passes and upsert into benchmarks_collected.csv
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

Each agent pass produces a JSON object `{"policy_periods": [...],
"annual_returns": [...]}` per `docs/agent_playbook.md`. Merge a single pass:

```
python3 scripts/merge_batch.py pass_a.json <batch-name>
```

Or reconcile two independent model passes for the same plan (the standard
path — see `docs/methodology.md`'s verification section):

```
python3 scripts/merge_batch.py pass_a.json <batch-name-a> pass_b.json <batch-name-b>
```

This upserts rows into `data/benchmarks_collected.csv` keyed by
`(ppd_id, fy)`, sets `cross_model_agreement` per row, and marks the
corresponding rows in `data/worklist.csv` as `done`.
