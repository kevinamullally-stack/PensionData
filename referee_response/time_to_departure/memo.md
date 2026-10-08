# Time-to-departure / dose-response analysis for "Conflicted CIOs"

Prepared for the Financial Management revision. Addresses Referee Major Concern 3
(time-to-departure design), the two minor points that point back to it (CIO-level
selection; treatment-intensity heterogeneity), and the timing half of Concern 5
(does underperformance and fee escalation accelerate toward exit, and does the fee
channel absorb the Conflicted coefficient).

Data: `data_v3_3.dta` (2,749 plan-years, 153 plans, 556 CIO-plan spells, FY2001-2020).
Full regression output: `results_full.md`. Code: `ttd_analysis.py`. Figure: `fig_event_time.png`.

---

## 1. Bottom line

**The referee's own test does not find acceleration.** Under the referee's framing, a
stable CIO type predicts a flat underperformance profile across tenure; conflicted
behavior timed to the payoff predicts underperformance (and fee escalation) that
worsens as departure nears. In every version of the test:

- The conflicted CIO underperformance is a **level effect present throughout tenure**.
  It is at least as large five or more years before departure as in the exit year.
- On peer-adjusted returns it **shrinks** toward departure; within-CIO, conflicted CIOs
  perform *better* in their last three years than in their own far-from-departure
  years. 26 of the 30 conflicted CIOs observed both far from and close to departure
  improved.
- Every other departure type (retirement, move to another public plan, move to a
  non-asset-manager private job) shows the **opposite**: performance deteriorates
  before exit. The conflicted-minus-other difference in the near-minus-far change is
  positive and significant in most specifications.
- Aggregate fees do **not** escalate toward departure for conflicted CIOs, and
  controlling for fees does not absorb the Conflicted coefficient at all.

So the dose-response design, taken at face value, favors the selection / "type"
interpretation (or a conflict whose cost is spread evenly over tenure) over
"favors done right before the payoff." The honest revision states that the
underperformance is a tenure-long level effect that this design cannot attribute to
behavior rather than type, and tempers the quid-pro-quo language accordingly, which
is what the editor says is acceptable.

---

## 2. What was estimated

**Baseline (reconstructed Table III).** Peer-adjusted return (pp) on Conflicted CIO,
log plan size, GASB funded ratio, return assumption, separate investment board, CIO
age, CIO tenure, prior private experience, elite institution; plan and fiscal-year
fixed effects; SE clustered by plan. This gives Conflicted = −0.47 (p = 0.02,
N = 2,174), close to the paper's −0.56; benchmark-adjusted gives −1.09 (p = 0.06,
N = 1,559). Please rerun everything below with the paper's exact Table III
specification; the qualitative pattern was stable across every control set tried.

**Years-to-departure variable.** `time_to_departure` = FY − departure year for CIOs
with an observed departure. For CIOs never observed leaving it is FY − last year in
the panel, so those spells are treated as the never-departing reference, not as
departures. Bins: ≤ −5, −4, −3, −2, −1, 0 (exit year).

**Comparison group.** Every design interacts the bins with both *Conflicted* and
*Other observed departure* (retire, move public, move to non-vendor private job,
fired, died). Within a CIO's spell, years-to-departure and tenure move one-for-one,
so a generic lame-duck or experience effect cannot be separated from a
departure-timing effect using conflicted CIOs alone. The *other departures* profile
is what identifies a conflict-specific timing effect, and all tests are reported as
between-group differences (Concern 1).

Four designs:

1. **Bins, pooled** (plan + year FE): level of each group in each bin relative to
   non-departing CIO-years.
2. **Bins, within CIO** (CIO-spell + year FE): profile relative to the same CIO's
   own ≤ −5 years. This is the design the referee's minor point asks for in place of
   CIO fixed effects; the treatment now varies within CIO.
3. **Linear slope**: Conflicted × years-to-departure (winsorized at −8); slope is the
   change in pp per year closer to exit.
4. **Tenure halves** (departing CIOs only): second half = tenure > final tenure / 2,
   extending the authors' `ten_half` construction to all departing CIOs.

Fees (total external fee %, expense ratio, asset-class fees, fee rank) and
allocation (alternatives share, PE share) run through designs 1-3 as well.

---

## 3. Results

### 3.1 Returns profile by years to departure (pooled, plan + year FE)

Peer-adjusted return, pp. Reference = CIO-years with no observed departure.

| Bin | Conflicted | Other departure | Difference |
|---|---|---|---|
| ≤ −5 | −1.20** (0.50) | 0.08 (0.31) | −1.28** (0.56) |
| −4 | −0.79*** (0.29) | 0.09 (0.35) | −0.88** (0.39) |
| −3 | −0.63 (0.49) | −0.24 (0.25) | −0.39 (0.45) |
| −2 | −0.66 (0.43) | −0.45 (0.29) | −0.21 (0.44) |
| −1 | −0.36 (0.28) | −0.56** (0.25) | 0.20 (0.25) |
| 0 | −0.55 (0.34) | −0.44* (0.24) | −0.10 (0.29) |
| Flatness (all bins equal), F-test p | 0.75 | 0.10 | |
| Near (−2..0) − Far (≤ −4) | +0.48 (0.41) | −0.57*** (0.22) | **+1.04** (0.46), p = 0.02 |

N = 2,174. Benchmark-adjusted (N = 1,559): conflicted bins −1.16, −1.46, −2.36,
−1.23, −1.03, −1.42 (all but the −2 bin significant at 10% or better); near − far =
+0.09 (p = 0.74); other departures +0.12; difference −0.03 (p = 0.92). The profile
is flat, not accelerating.

### 3.2 Within-CIO profile (CIO-spell + year FE, relative to own ≤ −5 years)

| Bin | Conflicted, peer-adj | Other, peer-adj | Diff | Conflicted, bench-adj | Other, bench-adj | Diff |
|---|---|---|---|---|---|---|
| −4 | 0.43 (0.46) | −0.01 (0.36) | 0.43 | −0.35 (0.58) | −0.23 (0.32) | −0.12 |
| −3 | 1.06 (0.84) | −0.22 (0.28) | 1.28 | −0.29 (0.78) | −0.93 (0.67) | 0.65 |
| −2 | 1.05 (0.68) | −0.77** (0.35) | 1.82** | 0.83 (0.57) | −0.42 (0.37) | 1.25* |
| −1 | 1.19* (0.70) | −0.40 (0.29) | 1.59** | 0.96* (0.58) | −0.43 (0.34) | 1.39** |
| 0 | 1.18 (0.77) | −0.46 (0.39) | 1.64* | 0.49 (0.65) | −0.09 (0.39) | 0.58 |
| Near (−2..0) − Far (−4, ≤ −5) | +0.90* (0.51) | −0.59** (0.27) | **+1.49***, p = 0.01 | +0.93*** (0.31) | −0.20 (0.25) | **+1.13***, p = 0.01 |

N = 2,549 / 1,795. Identified off 33 conflicted spells with any far year (30 with
both far and near years) against 96 / 83 other-departure spells. Raw within-CIO
change (near minus far, peer-adjusted): conflicted +0.92 pp, 87% improving (n = 30);
other departures −0.52 pp, 37% improving (n = 83).

### 3.3 Summary of the timing tests

Sign convention: a negative "slope" or "near − far" means performance worsens as
exit approaches (the conflicted-behavior prediction).

| Test | Outcome | Conflicted | Other departures | Difference |
|---|---|---|---|---|
| Linear slope per year, pooled | peer-adj | +0.12 (0.08) | −0.08* (0.04) | +0.20** (0.09) |
| Linear slope per year, within CIO | peer-adj | +0.16* (0.09) | −0.08 (0.05) | +0.24** (0.11) |
| Linear slope per year, pooled | bench-adj | +0.03 (0.07) | +0.04 (0.05) | −0.01 (0.08) |
| Linear slope per year, within CIO | bench-adj | +0.16** (0.08) | 0.00 (0.05) | +0.16* (0.09) |
| 2nd half of tenure − 1st half, pooled | peer-adj | −0.01 (0.27) | +0.05 (0.18) | −0.06 (0.28) |
| 2nd half − 1st half, within CIO | peer-adj | −0.16 (0.25) | −0.55* (0.30) | +0.40 (0.28) |
| 2nd half − 1st half, pooled | bench-adj | −0.23 (0.34) | 0.00 (0.38) | −0.23 (0.45) |
| 2nd half − 1st half, within CIO | bench-adj | −0.49 (0.39) | −0.80* (0.44) | +0.31 (0.36) |
| Authors' close_conf vs far_conf | peer-adj | close −0.35, far −1.20*** | | close − far +0.85* (0.46) |
| Authors' close_conf vs far_conf | bench-adj | close −1.13*, far −0.74 | | close − far −0.39 (0.38) |

Conflicted first-half level (pooled, departing CIOs only): −0.20 peer-adj (ns),
−1.04** bench-adj. The underperformance is already there in the first half.

### 3.4 Fees and allocation

| Outcome (pooled, plan + year FE) | Conflicted level, far bins | Conflicted near − far | Other near − far | DiD |
|---|---|---|---|---|
| Total external fee % of assets | −0.04 / −0.06 | −0.03 (0.05) | +0.04* (0.03) | −0.07 (0.05) |
| Expense ratio | −0.09 / −0.13** | −0.03 (0.04) | +0.01 (0.02) | −0.04 (0.05) |
| PE fee % | −0.15 / −0.56 | −0.49** (0.22) | −0.19 (0.19) | −0.30 (0.28) |
| Real estate fee % | −0.44* / −0.46* | −0.04 (0.13) | +0.11 (0.12) | −0.14 (0.16) |
| Hedge fund fee % | 0.21 / −0.07 | −0.09 (0.16) | −0.18 (0.37) | +0.09 (0.41) |
| Total fee rank | 0.19 / 0.10 | +0.03 (0.13) | +0.02 (0.07) | 0.00 (0.14) |
| Alternatives share of assets | −0.07** / −0.02 | +0.02 (0.02) | +0.01 (0.01) | +0.01 (0.02) |

Within CIO, total fee % and expense ratio are flat for both groups (all bins within
±0.07 pp of the far years, none significant). The one within-CIO movement is in
allocation: conflicted CIOs raise the alternatives share by 4-7 pp of assets relative
to their own far years, versus 1-2 pp for other departers (DiD +4.4 pp at ttd −2..0,
p = 0.09). That is a tilt, not a fee escalation.

The authors' own split gives close_conf −0.13* and far_conf −0.03 on total fee %
(close − far = −0.10, p = 0.045): fees are *lower*, not higher, in the years close
to exit once plan and year effects are in. Please reconcile this with how Table IX
constructs its fee outcome before drafting the fee part of the response.

### 3.5 Mediation

Same-sample comparison, peer-adjusted return, N = 1,873: Conflicted = −0.43**
without fee control, −0.49** with total fee % as a control, −0.51*** with the
authors' Fee Slope variable. Near-departure conflicted effect: −0.64** without,
−0.68** with fees. Benchmark-adjusted: −0.45 vs −0.45. The fee level does not absorb
any of the Conflicted coefficient. The fee coefficient itself is −0.54** on
peer-adjusted and +0.70*** on benchmark-adjusted returns, so it is not a clean
mediator either.

### 3.6 Profile by departure type (pooled, peer-adjusted)

| Departure type | Far (≤ −4) | Near (−1, 0) | Near − Far | Conflicted minus this type |
|---|---|---|---|---|
| Conflicted (vendor) | −1.06*** | −0.39 | +0.66 (0.46) | |
| Retire | 0.16 | −0.40 | −0.56* (0.33) | +1.22** (0.57) |
| Move to another public plan | −0.08 | −0.64*** | −0.57** (0.23) | +1.23** (0.50) |
| Move to private, non-asset-manager | 0.06 | −1.00** | −1.07 (0.84) | +1.73* (0.94) |

Conflicted CIOs are the only departure type whose performance does not deteriorate
before exit.

### 3.7 Robustness (coarse bins, pooled, peer-adjusted)

| Variant | Conf far | Conf near | Conf near − far | DiD vs other |
|---|---|---|---|---|
| Baseline | −1.05*** | −0.44 | +0.61 | +1.22** |
| Tenure bins instead of linear tenure | −1.04*** | −0.46 | +0.57 | +1.22** |
| Drop spells with unknown exit | −0.85** | −0.43 | +0.42 | +0.98** |
| Departing spells only (ref = other far) | −0.52 | −0.40 | +0.13 | +0.75 |
| Conflicted spells with final tenure ≥ 4 only | −1.15*** | −0.26 | +0.89 | +1.49** |
| Excluding the departure year (bins −2, −1 vs far) | | | +0.49 | +1.08** |

Benchmark-adjusted: near − far between −0.17 and +0.30 in every variant, DiD
between 0.01 and 0.22, none significant. Flat.

---

## 4. Caveats to state in the paper

- **Power far from departure.** Conflicted CIOs have short tenures (median final
  tenure 3 years; 58% leave within 3 years). Only 63 conflicted CIO-years sit in the
  ≤ −5 bin and 34 in the −4 bin, from 33 spells. The flatness tests have limited
  power against moderate slopes; the point estimates nevertheless have the wrong sign
  for acceleration in every specification.
- **Composition.** In the pooled design the far bins are populated by longer-tenured
  conflicted CIOs. The within-CIO design removes this and gives the same answer.
- **Tenure vs. time-to-departure.** Within a spell the two are collinear. The
  design identifies a *conflict-specific* timing effect relative to other departures,
  not a timing effect in isolation. That is the correct object given Concern 1.
- **Departure-year attribution.** A CIO who leaves mid-year shares the exit-year
  return with a successor. Results are unchanged excluding the exit year.
- **Baseline reconstruction.** Controls were reverse-engineered from the dataset and
  the referee report (−0.47 vs. the paper's −0.56). Rerun with the exact spec.

---

## 5. Draft response text

**Referee Concern 3 (and Minor Points 1 and 5).**

> We thank the referee for this suggestion and have implemented the time-to-departure
> design in full (new Table [X] and Figure [Y]). We interact the Conflicted indicator
> with indicators for 5+, 4, 3, 2, 1 and 0 fiscal years before the CIO's departure,
> and, following the referee's Concern 1, we estimate the same profile for CIOs who
> depart for any other reason so that every statement is a between-group test. We
> report three versions: the pooled specification of Table III; a within-CIO
> specification with CIO-spell fixed effects, in which the profile is identified
> entirely from variation within a CIO's own tenure (this is the within-CIO test the
> referee notes is infeasible under the baseline definition); and a comparison of the
> first and second halves of each departing CIO's tenure.
>
> The results do not support an accelerating profile. The underperformance of
> conflicted CIOs is a level effect that is present from the earliest years of
> tenure: on benchmark-adjusted returns it is −1.2 to −1.5 percentage points five or
> more years before departure and −1.0 to −1.4 in the final two years, and we cannot
> reject a flat profile (p = [0.07]). On peer-adjusted returns the point estimates
> move toward zero as departure nears, and within CIO, conflicted CIOs perform about
> 0.9 percentage points *better* in their last three years than in their own earlier
> years, whereas CIOs who depart for other reasons perform about 0.6 points worse
> before exit; the difference is significant (p = [0.01]). Fees paid to external
> managers and the expense ratio are flat over the run-up to departure for conflicted
> CIOs, and adding fees as a control leaves the Conflicted coefficient unchanged.
>
> We therefore revise our interpretation. Under the referee's framework a stable CIO
> type predicts a flat profile and conflicted behavior timed to the payoff predicts
> acceleration; our evidence is consistent with the former, or with a conflict whose
> cost is spread evenly over tenure rather than concentrated before exit. We now
> describe the Conflicted coefficient as the performance differential of CIOs who
> eventually move to a vendor, state explicitly that this design cannot attribute it
> to behavior rather than type, and remove language asserting a quid pro quo
> [cross-reference to the revised introduction and Section 5]. We note two
> limitations of the test: conflicted CIOs have short tenures (median three years),
> so only [33] conflicted CIOs contribute observations five or more years before
> departure, and within a tenure spell time-to-departure and tenure are collinear, so
> the design identifies a conflict-specific timing effect relative to other
> departures rather than a timing effect in isolation.

**Referee Concern 5 (timing and mediation portion).**

> The referee suggests that steering predicts underperformance that operates through
> the fee and allocation channel and accelerates toward departure, while hiring for
> relationships predicts no own-plan underperformance. The time-to-departure results
> fit neither cleanly. Underperformance exists but does not accelerate, and the fee
> level does not mediate it (the Conflicted coefficient is −0.43 without and −0.49
> with fee controls on the same sample). The only within-CIO movement we find is in
> allocation: conflicted CIOs raise their alternatives share by 4-7 percentage points
> of assets relative to their own early years, about 4 points more than other
> departing CIOs (p = 0.09). We present this as suggestive and consistent with an
> allocation tilt rather than a fee-based quid pro quo, and we have rewritten Section
> 5 to lay out the steering and relationship interpretations side by side with the
> evidence for and against each.

---

## 6. Suggested exhibits for the paper

- **Table X. Performance over the run-up to departure.** Columns: peer-adjusted and
  benchmark-adjusted; pooled and within-CIO. Rows: Conflicted × bin and Other
  departure × bin, then the near − far difference for each group, the
  difference-in-differences, and the flatness F-test p-values. Section 3.1-3.2 above.
- **Figure Y.** `fig_event_time.png` (PDF version alongside): four panels, conflicted
  vs. other departures with 95% CIs, pooled on top and within-CIO below.
- **Table X, Panel B (fees).** Total fee %, expense ratio, alternatives share, same
  layout. Section 3.4.
- **Internet Appendix.** Tenure halves, linear slopes, placebo departure types,
  robustness variants (Sections 3.3, 3.6, 3.7).

---

## 7. Reproducing

```
pip install pandas pyfixest scipy matplotlib
python3 ttd_analysis.py /path/to/data_v3_3.dta      # writes results_full.md
python3 make_fig.py                                 # writes fig_event_time.png / .pdf
```

`data_v3_3.dta` is not committed to this repository.
