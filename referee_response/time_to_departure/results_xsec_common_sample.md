Common sample (peer-adj and bench-adj both non-missing): 1329 plan-years, 121 plans, conflicted share 0.175 | full Table III sample: 1948 plan-years, 144 plans, conflicted share 0.188
Dependent variables: Peer-adj; Bench-adj; Gap = Bench-adj minus Peer-adj = (peer average return - plan's own benchmark return). Year FE, controls interacted with the split as in the do-file, SE double clustered by plan & year.

## Table III baseline (col 1 spec: base controls, year FE), common sample
  Peer-adj   Conflicted  -0.614***(-3.07) N=1240
  Bench-adj  Conflicted  -0.518** (-2.65) N=1240
  Gap        Conflicted   0.096   ( 0.34) N=1240

## Underpaid (split on underpaid)
sample / dependent variable                  Underpaid x Conf         Not underpaid x Conf     p(equal)  N
Full sample / Peer-adj                        -0.870***(-4.27)         -0.394   (-1.51)        0.101     1495
Full sample / Bench-adj                       -0.674*  (-1.75)         -0.474   (-1.72)        0.658     1061
Common sample / Peer-adj                      -1.167***(-3.83)         -0.377   (-1.18)        0.040     1061
Common sample / Bench-adj                     -0.674*  (-1.75)         -0.474   (-1.72)        0.658     1061
Common sample / Gap (bench - peer)             0.493   ( 1.55)         -0.097   (-0.31)        0.235     1061

## Young (split on young)
sample / dependent variable                  Young x Conf             Not young x Conf         p(equal)  N
Full sample / Peer-adj                        -1.216***(-3.52)         -0.370*  (-1.90)        0.050     1621
Full sample / Bench-adj                       -0.871***(-3.07)         -0.618** (-2.28)        0.587     1158
Common sample / Peer-adj                      -1.722***(-3.30)         -0.335   (-1.32)        0.048     1158
Common sample / Bench-adj                     -0.871***(-3.07)         -0.618** (-2.28)        0.587     1158
Common sample / Gap (bench - peer)             0.851*  ( 1.86)         -0.283   (-1.19)        0.019     1158

## High discount rate (split on highrate)
sample / dependent variable                  High rate x Conf         Low rate x Conf          p(equal)  N
Full sample / Peer-adj                        -1.409   (-1.45)         -0.382   (-1.26)        0.419     1552
Full sample / Bench-adj                       -0.849   (-1.10)         -0.339*  (-1.98)        0.535     1116
Common sample / Peer-adj                      -1.276   (-1.43)         -0.437   (-1.41)        0.427     1116
Common sample / Bench-adj                     -0.849   (-1.10)         -0.339*  (-1.98)        0.535     1116
Common sample / Gap (bench - peer)             0.428   ( 0.31)          0.098   ( 0.35)        0.830     1116

## High funding (split on highfund)
sample / dependent variable                  High funding x Conf      Low funding x Conf       p(equal)  N
Full sample / Peer-adj                        -1.341***(-7.03)         -0.322** (-2.14)        0.000     1667
Full sample / Bench-adj                       -1.301** (-2.19)         -0.442   (-1.66)        0.249     1203
Common sample / Peer-adj                      -1.802** (-2.44)         -0.361** (-2.21)        0.046     1203
Common sample / Bench-adj                     -1.301** (-2.19)         -0.442   (-1.66)        0.249     1203
Common sample / Gap (bench - peer)             0.500   ( 1.04)         -0.081   (-0.24)        0.340     1203

## Financial center (split on fincenter1)
sample / dependent variable                  Fin. center x Conf       Not fin. center x Conf   p(equal)  N
Full sample / Peer-adj                        -0.027   (-0.09)         -0.612** (-2.57)        0.157     1567
Full sample / Bench-adj                       -0.673*  (-2.05)         -0.456*  (-1.85)        0.594     1127
Common sample / Peer-adj                       0.264   ( 0.96)         -0.731*  (-2.06)        0.056     1127
Common sample / Bench-adj                     -0.673*  (-2.05)         -0.456*  (-1.85)        0.594     1127
Common sample / Gap (bench - peer)            -0.937***(-4.30)          0.275   ( 1.06)        0.002     1127

## Prior private experience (split on prior_private_exp)
sample / dependent variable                  Prior private x Conf     No prior private x Conf  p(equal)  N
Full sample / Peer-adj                        -0.266   (-1.05)         -0.774** (-2.30)        0.348     1484
Full sample / Bench-adj                       -0.817*  (-1.81)         -0.447   (-1.31)        0.535     1073
Common sample / Peer-adj                      -0.232   (-0.78)         -0.996** (-2.81)        0.155     1073
Common sample / Bench-adj                     -0.817*  (-1.81)         -0.447   (-1.31)        0.535     1073
Common sample / Gap (bench - peer)            -0.584** (-2.26)          0.549   ( 1.47)        0.004     1073

## Raw means of Gap (peer avg - own benchmark, pp) in the common sample: conflicted vs non-conflicted, by subgroup
  Underpaid                  Underpaid       : conf   0.71 non-conf   0.20 | Not underpaid   : conf  -0.16 non-conf   0.06
  Young                      Young           : conf   0.77 non-conf   0.23 | Not young       : conf  -0.06 non-conf   0.08
  High discount rate         High rate       : conf   0.07 non-conf  -0.22 | Low rate        : conf   0.36 non-conf   0.17
  High funding               High funding    : conf   0.77 non-conf  -0.00 | Low funding     : conf   0.21 non-conf   0.17
  Financial center           Fin. center     : conf  -1.20 non-conf   0.02 | Not fin. center : conf   0.67 non-conf   0.15
  Prior private experience   Prior private   : conf  -0.10 non-conf   0.34 | No prior private: conf   0.84 non-conf   0.09