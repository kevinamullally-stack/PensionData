# Benchmark returns: conflicted vs unconflicted CIOs, and across cross-sectional groups
Sample: Table III sample (cio_dum==1, fy<=2020, curr1==0) with a hand-collected policy benchmark: 1329 plan-years, 121 plans, 233 conflicted plan-years.
Dependent variable: plan's total-fund policy benchmark return (pp). All regressions absorb fiscal-year-end date (fye1) effects, so comparisons are within plans sharing the same 12-month window. SE double clustered by plan and fiscal year; t in parentheses.

## Table B1. Policy benchmark return, Conflicted vs unconflicted
col | controls | plan FE | Conflicted coef (t) | N | adj R2
(1) | target wts: No, Table III ctrls: No | plan FE No |  -0.153   (-0.56) | 1320 | 0.919
(2) | target wts: Yes, Table III ctrls: No | plan FE No |   0.002   ( 0.01) | 1293 | 0.923
(3) | target wts: Yes, Table III ctrls: Yes | plan FE No |  -0.000   (-0.00) | 1064 | 0.933
(4) | target wts: Yes, Table III ctrls: Yes | plan FE Yes |  -0.096   (-0.15) | 1061 | 0.933
Descriptive: mean benchmark return minus same-fye1 peer average: conflicted -0.118, unconflicted 0.025 (pp)

## Table B2A. Policy benchmark return by cross-sectional group (without target-weight controls; do-file controls interacted with the split; fye1 FE)
split                      group x Conflicted       other group x Conflicted p(equal) N
Underpaid                   -0.411   (-1.00)          0.251   ( 0.71)        0.252    1054
Young                       -0.855*  (-1.82)          0.352   ( 1.54)        0.013    1150
High funding                -0.285   (-0.56)          0.223   ( 0.65)        0.408    1196
Financial center             0.730***( 3.06)         -0.124   (-0.40)        0.036    1120
Prior private experience     0.694** ( 2.43)         -0.517   (-1.15)        0.008    1066
High discount rate          -0.435   (-0.43)          0.059   ( 0.19)        0.640    1109

## Table B2B. Policy benchmark return by cross-sectional group (with target-weight controls; do-file controls interacted with the split; fye1 FE)
split                      group x Conflicted       other group x Conflicted p(equal) N
Underpaid                   -0.660   (-1.48)          0.111   ( 0.41)        0.161    1052
Young                       -0.393   (-1.20)          0.236   ( 1.00)        0.214    1149
High funding                -0.756   (-1.48)          0.162   ( 0.50)        0.190    1192
Financial center             0.417   ( 1.32)         -0.185   (-0.66)        0.188    1119
Prior private experience     0.439*  ( 1.95)         -0.556   (-1.28)        0.009    1065
High discount rate          -0.243   (-0.49)         -0.091   (-0.32)        0.788    1108

## Table B3. Among conflicted CIOs only: policy benchmark return on the group indicator (fye1 FE)
group indicator            (1) no controls            (2) + target weights       (3) + Table III controls  
Underpaid (0/1)             -0.602   (-0.86)  N=224    -0.539   (-0.65)  N=212     0.707   ( 1.19)  N=177  
Young (0/1)                 -0.601   (-1.21)  N=226    -0.464   (-0.73)  N=214    -0.371   (-0.50)  N=179  
High Funding (0/1)          -0.647   (-1.39)  N=225    -0.235***(-24.94) N=213    -0.628   (-1.59)  N=179  
Financial Center (0/1)       1.527*  ( 1.77)  N=226     1.857   ( 1.26)  N=214     1.173   ( 1.17)  N=179  
Prior Private Exp. (0/1)     1.078*  ( 1.97)  N=220     0.927*  ( 1.92)  N=208     0.927   ( 1.37)  N=179  
High Discount Rate (0/1)     0.172   ( 0.24)  N=215     0.006   ( 0.01)  N=203     0.009   ( 0.02)  N=172  

## Table B4. Asset-class benchmark (index) returns, conflicted vs unconflicted (fye1 FE; (1) no controls, (2) target weights + Table III controls)
  U.S. equity                   -0.076   (-0.76) N=1378 |  -0.109   (-1.41) N=1046   (sd within fye1: 1.37)
  Intl equity                   -0.246   (-1.36) N=1343 |  -0.597** (-2.33) N=1029   (sd within fye1: 1.87)
  Fixed income                   0.140   ( 0.66) N=1635 |   0.307   ( 1.46) N=1282   (sd within fye1: 1.57)
  Real estate                    0.025   ( 0.11) N=1088 |   0.290   ( 0.79) N=894   (sd within fye1: 4.48)
  Private equity                -2.868** (-2.12) N=878 |  -1.686   (-1.57) N=782   (sd within fye1: 8.21)
  Hedge funds                   -0.531   (-1.54) N=470 |  -1.314** (-2.90) N=413   (sd within fye1: 3.96)
  Total fund (collected file)   -0.192   (-1.19) N=1410 |   0.015   ( 0.10) N=1115   (sd within fye1: 1.82)

## Table B5. Asset-class benchmark returns by cross-sectional group (fye1 FE; target weights + do-file controls interacted): group x Conf | other x Conf | p(equal)
  Underpaid:
    U.S. equity       -0.066   (-0.47)         -0.098   (-1.34)        0.823    N=1051
    Intl equity       -0.582** (-2.15)          0.428   ( 0.87)        0.084    N=1034
    Fixed income       0.453   ( 1.47)         -0.101   (-0.36)        0.170    N=1280
    Real estate        0.077   ( 0.15)          0.122   ( 0.23)        0.952    N=890
    Private equity    -1.260   (-0.66)         -1.785   (-0.86)        0.820    N=754
    Hedge funds        0.062   ( 0.07)         -1.394   (-0.94)        0.397    N=376
  Young:
    U.S. equity       -0.243   (-1.28)         -0.051   (-0.72)        0.353    N=1127
    Intl equity       -0.994***(-4.13)         -0.078   (-0.24)        0.007    N=1110
    Fixed income       0.194   ( 0.71)          0.099   ( 0.30)        0.780    N=1384
    Real estate        1.151*  ( 1.97)         -0.698***(-4.84)        0.012    N=972
    Private equity    -0.120   (-0.06)         -2.584   (-1.58)        0.311    N=806
    Hedge funds       -0.921   (-0.45)          0.827   ( 1.35)        0.493    N=427
  High funding:
    U.S. equity        0.194   ( 0.63)         -0.153   (-1.18)        0.381    N=1186
    Intl equity        1.037*  ( 1.92)         -0.504** (-2.14)        0.026    N=1161
    Fixed income      -0.118   (-0.26)          0.308   ( 1.10)        0.286    N=1431
    Real estate        0.216   ( 0.22)         -0.590   (-0.85)        0.571    N=975
    Private equity    -6.172   (-1.44)         -1.419   (-1.35)        0.294    N=831
    Hedge funds          n/a                   -0.058   (-0.12)                 N=454
  Financial center:
    U.S. equity       -0.004   (-0.04)         -0.104   (-1.13)        0.556    N=1099
    Intl equity       -0.647   (-0.87)         -0.296   (-1.10)        0.689    N=1082
    Fixed income       0.001   ( 0.01)          0.307   ( 0.86)        0.442    N=1349
    Real estate        3.177***( 3.98)          0.204   ( 0.45)        0.000    N=939
    Private equity   -10.562***(-6.70)         -1.180   (-1.00)        0.000    N=802
    Hedge funds        0.831   ( 0.94)         -1.241   (-1.74)        0.119    N=423
  Prior private experience:
    U.S. equity       -0.056   (-0.70)         -0.118   (-1.02)        0.633    N=1047
    Intl equity       -0.758** (-2.26)         -0.604*  (-1.75)        0.730    N=1030
    Fixed income       0.421   ( 1.38)          0.336   ( 1.04)        0.846    N=1283
    Real estate        0.818   ( 1.09)          0.153   ( 0.34)        0.488    N=895
    Private equity    -0.295   (-0.22)         -2.599** (-2.79)        0.207    N=783
    Hedge funds       -1.321*  (-1.79)         -2.453   (-1.25)        0.648    N=414