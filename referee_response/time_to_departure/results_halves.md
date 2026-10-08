counts: conflicted CIO-years first/second half: [166, 142] | distinct conflicted CIOs: 41 | other departers CIOs: 137

=== 1. Halves with tenure at departure; clustering by plan / CIO / system ===
outcome  FE           cluster  | conf 2nd-1st       other 2nd-1st      difference         95% CI diff
ret100   ppd_id + fy  ppd_id   |   0.01   (0.31)     -0.25   (0.23)      0.26   (0.32)    [-0.37, 0.90]  N=949
ret100   ppd_id + fy  cio      |   0.01   (0.38)     -0.25   (0.27)      0.26   (0.44)    [-0.60, 1.13]  N=949
ret100   ppd_id + fy  system_id |   0.01   (0.44)     -0.25   (0.28)      0.26   (0.42)    [-0.58, 1.11]  N=949
ret100   spell + fy   ppd_id   |  -0.26   (0.30)     -0.90***(0.31)      0.64*  (0.32)    [-0.00, 1.28]  N=1067
ret100   spell + fy   cio      |  -0.26   (0.39)     -0.90** (0.37)      0.64   (0.42)    [-0.20, 1.47]  N=1067
ret100   spell + fy   system_id |  -0.26   (0.37)     -0.90***(0.34)      0.64   (0.39)    [-0.14, 1.42]  N=1067
bret100  ppd_id + fy  ppd_id   |  -0.63   (0.41)     -0.28   (0.35)     -0.36   (0.49)    [-1.33, 0.61]  N=679
bret100  ppd_id + fy  cio      |  -0.63   (0.43)     -0.28   (0.38)     -0.36   (0.52)    [-1.38, 0.67]  N=679
bret100  ppd_id + fy  system_id |  -0.63   (0.49)     -0.28   (0.39)     -0.36   (0.61)    [-1.57, 0.86]  N=679
bret100  spell + fy   ppd_id   |  -0.66   (0.41)     -1.11** (0.42)      0.45   (0.34)    [-0.23, 1.12]  N=754
bret100  spell + fy   cio      |  -0.66   (0.47)     -1.11** (0.55)      0.45   (0.37)    [-0.30, 1.19]  N=754
bret100  spell + fy   system_id |  -0.66   (0.43)     -1.11** (0.43)      0.45   (0.31)    [-0.17, 1.07]  N=754

=== 2. Person-level paired test: each CIO's mean return in 2nd half minus 1st half (plans averaged within CIO-year) ===
ret100   conflicted      : n= 27 mean change  -0.15 median   0.15 share improving 0.56 | paired t p=0.746  Wilcoxon p=0.991  sign p=0.701
ret100   other departers : n= 89 mean change  -0.64 median  -0.06 share improving 0.44 | paired t p=0.078  Wilcoxon p=0.174  sign p=0.289
ret100   conflicted minus other change:   0.49  Welch p=0.400  Mann-Whitney p=0.437
bret100  conflicted      : n= 19 mean change   0.03 median   0.16 share improving 0.58 | paired t p=0.914  Wilcoxon p=0.922  sign p=0.648
bret100  other departers : n= 71 mean change  -0.55 median  -0.23 share improving 0.39 | paired t p=0.106  Wilcoxon p=0.138  sign p=0.096
bret100  conflicted minus other change:   0.59  Welch p=0.194  Mann-Whitney p=0.330

=== 3. Continuous: fraction of tenure elapsed (0=start, 1=departure); coefficient = change from start to end of tenure ===
ret100   ppd_id + fy  | conf   0.32   (0.54)    other  -0.02   (0.34)    diff   0.34   (0.62)    N=949
ret100   spell + fy   | conf   0.11   (0.51)    other  -0.71   (0.51)    diff   0.82   (0.60)    N=1066
bret100  ppd_id + fy  | conf  -0.20   (0.61)    other   0.40   (0.56)    diff  -0.60   (0.75)    N=679
bret100  spell + fy   | conf  -0.11   (0.64)    other  -0.25   (0.59)    diff   0.14   (0.63)    N=753

=== 4. Cleaner contrasts ===
ret100   tenure>=4 only, within CIO: conf 2nd-1st   0.17   (0.48)    diff vs other   0.94*  (0.50)    N=842  (conf CIOs 25)
ret100   last 2 yrs vs earlier, within CIO: conf   0.30   (0.40)    diff vs other   0.56   (0.46)    N=1067
bret100  tenure>=4 only, within CIO: conf 2nd-1st  -1.48*  (0.87)    diff vs other  -0.04   (0.49)    N=583  (conf CIOs 25)
bret100  last 2 yrs vs earlier, within CIO: conf   0.22   (0.59)    diff vs other   0.30   (0.63)    N=754

=== 5. Randomization inference: permute 'conflicted' across departing CIOs (person level), within-CIO halves DiD ===
observed DiD (peer-adj, within CIO) = 0.64; RI two-sided p = 0.176; one-sided p(DiD <= obs, i.e. acceleration) = 0.920; 500 permutations

=== 6. Equivalence bounds: largest conflicted-specific second-half deterioration the 95% CI allows (within CIO, cluster by CIO) ===
ret100  : conf own change 95% CI [-1.02, 0.50] | DiD 95% CI [-0.20, 1.47]  -> can rule out a conflict-specific deterioration larger than 0.20 pp
bret100 : conf own change 95% CI [-1.59, 0.27] | DiD 95% CI [-0.30, 1.19]  -> can rule out a conflict-specific deterioration larger than 0.30 pp

=== 7. Stacked asset-class peer-adjusted returns (eq, fi, re, pe, hf), asset x year and plan x asset FE, cluster by CIO ===
all classes pooled, plan x asset FE: conf level  -0.49   (0.40) conf 2nd-1st  -0.58   (0.38) diff vs other  -0.34   (0.46) N=4000
all classes pooled, spell x asset FE:  conf 2nd-1st  -0.92*  (0.47) diff vs other  -0.22   (0.48) N=3752
  eq : conf level  -0.13   (0.36) conf 2nd-1st  -0.17   (0.36) diff vs other   0.10   (0.44) N=1032
  fi : conf level   0.43   (0.36) conf 2nd-1st  -0.68   (0.52) diff vs other  -1.28** (0.62) N=1010
  re : conf level  -1.11   (1.44) conf 2nd-1st  -1.23   (1.57) diff vs other  -1.23   (1.72) N=792
  pe : conf level  -1.20   (1.35) conf 2nd-1st  -0.20   (1.75) diff vs other   1.35   (2.00) N=716
  hf : conf level  -1.41*  (0.82) conf 2nd-1st   0.17   (0.94) diff vs other   0.67   (1.13) N=450
