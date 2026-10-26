# Draft response: mechanism (steering vs. flat and fee-neutral)

**Referee comment.** "There are several robustness checks scattered about that they might be able to bring together to give a better idea of the mechanism. Does the underperformance operate through the fee/allocation channel and accelerate toward departure (steering), or is it flat and fee-neutral (benign)? A mediation-style test (does Fee Slope absorb the Conflicted coefficient?) is one way to think about it. The caveat is that these tests would have small subsamples."

**Response (draft).**

We thank the referee for this suggestion. We now bring the relevant evidence together in a new table (Table [X], "Steering or flat?"). We also add the mediation test the referee proposes (Table [Y]). The evidence points clearly in one direction: conflicted CIOs' underperformance is present from the start of their tenure, does not build up as departure approaches, and does not run through fee levels, fee trends or asset allocation.

*1. Does the fee or allocation channel absorb the Conflicted coefficient?*

Table [Y] re-estimates Table III on the plan-years with fee and allocation data. It then adds three candidate mediators one at a time and together: the Fee Ratio, the Fee Slope used in Table IX, and the share of assets in alternatives.

- **The Conflicted coefficient does not move.**
  - Peer-adjusted returns, fiscal-year-end fixed effects: −0.52 with the Table III controls, and −0.52, −0.56, −0.52 and −0.56 with the Fee Ratio, Fee Slope, alternatives share and all three added.
  - Benchmark-adjusted returns: −0.34 with the Table III controls, and −0.34 to −0.35 with the mediators.
  - A plan-level block bootstrap shows that none of these changes differs from zero (p-values 0.57–0.92).
  - With all three mediators added to the peer-adjusted regression, the 95% interval for the change is [−0.11, +0.16]. The fee and allocation variables therefore account for at most about 30% of the coefficient, and the point estimate is about zero.
- **Conflicted CIOs do have steeper Fee Slopes, as in Table IX.**
  - The CIO-plan Fee Slope is 0.09 higher (p = 0.016), and the median difference is also significant (rank-sum p = 0.016).
  - With the Table III controls, the difference is +0.14 (t = 2.4).
  - But the Fee Slope does not predict returns: its coefficient is positive and insignificant in every specification. It therefore cannot mediate the return shortfall.
- **Fee levels and allocations don't explain it either.**
  - Conflicted CIOs do not have higher Fee Ratios (−0.04, p = 0.44).
  - They hold less in alternatives, not more (−3.9 pp, p = 0.02).
  - Adding the lagged allocation controls to the Table III regression does not shrink the Conflicted coefficient: −0.41 without them, −0.52 with them.

*2. Does the underperformance accelerate toward departure?*

Table [X], Panel B, gives four tests for returns, the Fee Ratio and the alternatives share.

- **Halves.** We split Conflicted CIO into the first and second half of the CIO's tenure at the plan.
  - Peer-adjusted returns: the two halves are the same (−0.50 and −0.53; difference p = 0.88).
  - Benchmark-adjusted returns: the first half is the worse one (−0.57 vs. −0.36).
  - Fee Ratio and alternatives share: the second half never exceeds the first (p = 0.41–0.89).
- **Within-CIO, equal-weighted.** Each conflicted CIO's own change from the first to the second half, compared with other departing CIOs, with CIO and fiscal-year-end fixed effects:
  - Returns: +0.32 (p = 0.34) peer-adjusted and +0.51 (p = 0.10) benchmark-adjusted. Conflicted CIOs' returns do not deteriorate relative to their own early years; if anything they improve.
  - Fee Ratio: +0.03 (p = 0.40).
  - Alternatives share: +0.16 (p = 0.88).
- **Spell-level slopes.** Conflicted CIOs' returns trend up, not down, over their tenure (+0.24 pp per year relative to other departing CIOs, p = 0.07).
- **Without the 2009–2014 shock years.** The 2009–2014 period attenuates the conflicted effect (Table VIII) and falls late in many tenures. The halves tests give the same answer on fiscal years through 2008 and when excluding 2009–2014 (Appendix Table [Z]). In those samples the conflicted effect is larger, up to about twice as large, in both halves.
- **Last-n-year definitions.** Table III's columns 5–6, which count only the last 5 or 10 years before departure as conflicted, give coefficients similar to the full definition.

*3. Interpretation.*

In the referee's terms, the underperformance is flat and fee-neutral rather than an escalation through fees or allocations. We do not think "benign" follows, for three reasons:

- The shortfall is economically large, about 0.5 pp of plan return per year, and it persists throughout the conflicted CIO's tenure.
- It shrinks sharply during the 2009–2014 period of heightened scrutiny of pension-manager relationships (Table VIII). An explanation based on skill or other benign differences would not predict that.
- A shortfall that does not show up in aggregate fee ratios or asset-class weights is consistent with channels inside asset classes, such as which managers and vehicles are selected and on what terms. Plan-level fee and allocation data are too coarse to capture these. [Authors: adjust this sentence to the mechanism the paper emphasizes.]

As the referee anticipates, these tests rely on small subsamples. In the full sample, the halves tests can reliably detect (80% power, 5% test) a second-half difference of about 0.6–0.8 pp, roughly the size of the conflicted effect itself. They therefore rule out a strong acceleration but not a modest one. We note this in the text.

*Notes for the authors (not for the letter).*

- **Tables.** [Y] = `mechanism_mediation.xlsx`, sheet "Mediation"; [X] = same file, sheet "Mechanism summary"; [Z] = `table3_conflicted_halves_preshock.xlsx`. Power figures are in `preshock_halves_power.xlsx`.
- **Benchmark-adjusted with plan fixed effects.** The mediation sample requires fee data (1,067 plan-years for benchmark-adjusted returns, against 1,313 in Table III). On that sample, the benchmark-adjusted Conflicted coefficient with plan and fiscal-year-end fixed effects is small (−0.06, t = −0.3), so that panel has little to mediate. The other three panels have significant Conflicted coefficients.
- **Fee Slope tails.** Fee Slope has a few extreme values (±2.2). Winsorizing it at 1%/99% gives the same Conflicted coefficients.
- **Fee Slope medians.** The Fee Slope difference survives medians with the authors' variable, which includes allocation controls (rank-sum p = 0.016). With a simple slope of the Fee Ratio on fiscal year and no controls, the median difference is zero (rank-sum p = 0.50) and the mean difference comes from a few short spells.
