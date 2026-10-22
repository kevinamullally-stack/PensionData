# First-half vs. second-half tests outside the 2009–2014 shock period: sample size and power

These tests re-estimate Table III with Conflicted CIO split into the first and second half of the CIO's tenure. They drop the shock years in two ways: fiscal years through 2008, or all years except 2009–2014. Counts below are for the column 1 estimation sample (Table III controls, fiscal-year-end fixed effects). Full detail is in `preshock_halves_power.xlsx`.

## The samples are small

| Peer-adjusted return | Full sample | Through FY2008 | Excl. FY2009–2014 |
|---|---:|---:|---:|
| Plan-years | 1,478 | 536 | 908 |
| Fiscal years (year clusters) | 19 | 7 | 13 |
| Conflicted plan-years | 283 | 125 | 171 |
| … first half / second half | 141 / 142 | 72 / 53 | 87 / 84 |
| Conflicted CIOs | 42 | 25 | 33 |
| Conflicted CIOs observed in both halves | 28 | 8 | 14 |
| Conflicted plan-years per CIO-plan tenure (median) | 4 | 2 | 2 |
| Tenure at departure, mean years | 4.7 | 6.0 | 5.4 |

Benchmark-adjusted returns have about 15–20% fewer observations. Through FY2008 that leaves 101 conflicted plan-years and 23 conflicted CIOs, only 6 of them observed in both halves.

- **Through FY2008:** the second-half comparison rests on 53 plan-years. The within-CIO comparison rests on 8 CIOs (6 for benchmark-adjusted returns).
- **Few year clusters:** with only 7 fiscal years, double-clustered inference uses 6 degrees of freedom, which inflates the critical values.
- **Short windows:** a typical conflicted CIO-plan tenure contributes only 2 plan-years once the shock years are dropped, against 4 in the full sample. Most CIOs therefore appear in only one half.
- **Selection:** CIOs who left before 2009 had longer tenures (6.0 years at departure vs. 4.7), so the pre-2009 sample is not a random subset of conflicted CIOs.

## Power is low

Minimum detectable second-minus-first difference, in percentage points, for a two-sided 5% test with 80% power:

| | Full sample | Through FY2008 | Excl. FY2009–2014 |
|---|---:|---:|---:|
| Peer-adjusted, columns 1–3 | 0.59–0.69 | 1.40–1.86 | 0.86–1.16 |
| Peer-adjusted, column 4 (conflicted only, CIO FE) | 1.77 | 4.56 | 3.10 |
| Benchmark-adjusted, columns 1–3 | 0.61–0.77 | 0.85–2.43 | 0.72–1.08 |
| Benchmark-adjusted, column 4 | 1.16 | 3.15 | 1.81 |

For scale, the Conflicted CIO coefficient itself is about −0.5 to −1.3 pp.

- **Through FY2008:** the tests could reliably detect only a second-half deterioration 1.4–1.9 pp larger than the first-half effect. That is larger than the entire conflicted effect.
- **Excluding FY2009–2014:** the threshold is about 0.9–1.2 pp, roughly the size of the whole effect.
- **Column 4:** the within-CIO tests on conflicted CIOs alone could detect only differences of 3–4.5 pp.

**Bottom line:** the estimated differences are small (−0.18 to +0.05 pp for peer-adjusted returns). These tests cannot rule out economically meaningful second-half differences; they can only rule out very large ones.
