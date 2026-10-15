
# Attribution of the benchmark gap (peer average return - own policy benchmark) by subgroup. Conflicted coefficients; fiscal-year x FYE-month FE; do-file controls interacted with the split; SE clustered plan & year.
# gap = alloc + select + inter + resid.  alloc: own target weights vs peer-average weights at class-average index returns.  select: own class index returns vs class average, at peer-average weights (independent of the plan's allocation).  resid: part of the benchmark not reproduced by target weights x class indexes.

## Underpaid:   Underpaid x Conf | Not underpaid x Conf | p(equal)
  Peer-adjusted               -0.446   (-1.47)       -0.442   (-1.11)      0.992   N=689
  Benchmark-adjusted          -0.685   (-1.57)       -0.722   (-1.42)      0.944   N=689
  Gap (total)                 -0.238   (-0.52)       -0.279   (-0.84)      0.946   N=689
    allocation effect         -0.480** (-2.38)       -0.168   (-0.72)      0.457   N=689
    index-selection effect     0.220   ( 0.47)       -0.013   (-0.05)      0.392   N=689
    interaction                0.175   ( 1.37)       -0.107   (-1.27)      0.088   N=689
    residual                  -0.153   (-0.40)        0.009   ( 0.02)      0.814   N=689

## Young:   Young x Conf | Not young x Conf | p(equal)
  Peer-adjusted               -1.123   (-1.32)       -0.157   (-0.87)      0.304   N=758
  Benchmark-adjusted          -0.940*  (-1.88)       -0.629** (-2.32)      0.528   N=758
  Gap (total)                  0.183   ( 0.35)       -0.471*  (-1.87)      0.169   N=758
    allocation effect         -0.010   (-0.03)       -0.208   (-1.46)      0.612   N=758
    index-selection effect     0.321*  ( 1.78)        0.113   ( 0.57)      0.493   N=758
    interaction                0.167   ( 1.17)       -0.006   (-0.09)      0.283   N=758
    residual                  -0.295   (-0.34)       -0.370   (-0.57)      0.902   N=758

## High funding:   High funding x Conf | Low funding x Conf | p(equal)
  Peer-adjusted               -2.013** (-2.58)       -0.272   (-1.26)      0.029   N=796
  Benchmark-adjusted          -1.839***(-3.05)       -0.798*  (-1.97)      0.147   N=796
  Gap (total)                  0.173   ( 0.39)       -0.526   (-1.34)      0.234   N=796
    allocation effect          0.106   ( 0.26)       -0.230*  (-1.94)      0.457   N=796
    index-selection effect     0.108   ( 0.34)        0.242*  ( 1.76)      0.654   N=796
    interaction                0.128   ( 0.85)       -0.019   (-0.29)      0.393   N=796
    residual                  -0.169   (-0.33)       -0.518   (-1.14)      0.470   N=796

## Financial center:   Fin. center x Conf | Not fin. center x Conf | p(equal)
  Peer-adjusted               -0.659** (-2.22)       -0.486*  (-1.92)      0.645   N=741
  Benchmark-adjusted          -1.547** (-2.66)       -0.638*  (-2.05)      0.236   N=741
  Gap (total)                 -0.888   (-1.39)       -0.153   (-0.47)      0.398   N=741
    allocation effect         -0.362   (-1.45)       -0.071   (-0.74)      0.344   N=741
    index-selection effect     0.384*  ( 2.01)        0.020   ( 0.16)      0.156   N=741
    interaction               -0.130   (-0.82)        0.011   ( 0.07)      0.483   N=741
    residual                  -0.780   (-1.48)       -0.113   (-0.33)      0.376   N=741

## Prior private experience:   Prior private x Conf | No prior private x Conf | p(equal)
  Peer-adjusted                0.122   ( 0.64)       -0.562*  (-1.92)      0.042   N=697
  Benchmark-adjusted          -0.861   (-1.73)       -0.576   (-0.91)      0.738   N=697
  Gap (total)                 -0.984*  (-1.89)       -0.014   (-0.02)      0.234   N=697
    allocation effect         -0.285   (-1.34)       -0.176   (-0.83)      0.717   N=697
    index-selection effect     0.096   ( 0.79)        0.194   ( 1.05)      0.685   N=697
    interaction               -0.153   (-0.99)        0.031   ( 0.29)      0.273   N=697
    residual                  -0.642   (-1.24)       -0.064   (-0.10)      0.495   N=697

## High discount rate:   High rate x Conf | Low rate x Conf | p(equal)
  Peer-adjusted               -0.962   (-1.55)       -0.293   (-1.24)      0.343   N=730
  Benchmark-adjusted          -0.945   (-1.39)       -0.398** (-2.60)      0.416   N=730
  Gap (total)                  0.017   ( 0.01)       -0.105   (-0.33)      0.931   N=730
    allocation effect          0.028   ( 0.22)       -0.115   (-0.99)      0.434   N=730
    index-selection effect     0.021   ( 0.07)        0.019   ( 0.19)      0.993   N=730
    interaction                0.399** ( 2.14)       -0.109   (-1.53)      0.016   N=730
    residual                  -0.431   (-0.80)        0.101   ( 0.37)      0.392   N=730

# Index selection by asset class: dependent variable = plan's own class benchmark return minus the class-year average (pp). Negative = softer index than peers. fiscal-year x FYE-month FE, base controls interacted; SE clustered plan & year.
Pooled (Table III col-1 style): conflicted coefficient on index-relative return:
  Equity           -0.131   (-0.79) N=801  (sd of dep var 1.27)
  Fixed income      0.040   ( 0.12) N=799  (sd of dep var 1.41)
  Real estate      -0.516   (-1.35) N=586  (sd of dep var 4.35)
  Private equity   -3.691*  (-2.08) N=497  (sd of dep var 8.21)
  Hedge funds       0.497   ( 1.04) N=271  (sd of dep var 4.21)

## Underpaid: index-relative return, Underpaid x Conf | Not underpaid x Conf | p(equal)
  Equity           -0.514** (-2.13)        0.121   ( 0.60)      0.035   N=737
  Fixed income      0.208   ( 0.75)       -0.222   (-0.42)      0.425   N=735
  Real estate      -0.633   (-1.49)       -0.034   (-0.06)      0.471   N=537
  Private equity   -5.575** (-2.70)       -3.566   (-1.68)      0.111   N=451
  Hedge funds      -0.939   (-0.55)        0.196   ( 0.14)      0.714   N=223

## Young: index-relative return, Young x Conf | Not young x Conf | p(equal)
  Equity           -0.015   (-0.07)       -0.083   (-0.44)      0.826   N=801
  Fixed income     -0.024   (-0.11)        0.060   ( 0.14)      0.838   N=799
  Real estate       1.245   ( 1.46)       -0.734** (-2.31)      0.047   N=586
  Private equity   -3.598   (-0.76)       -3.771*  (-1.86)      0.971   N=497
  Hedge funds       3.188   ( 1.05)        0.455   ( 0.82)      0.406   N=271

## High funding: index-relative return, High funding x Conf | Low funding x Conf | p(equal)
  Equity            0.005   ( 0.02)       -0.202   (-1.18)      0.496   N=801
  Fixed income     -0.265   (-0.34)        0.076   ( 0.26)      0.585   N=799
  Real estate       2.704   ( 1.33)       -0.781** (-2.17)      0.114   N=586
  Private equity   -3.002   (-0.48)       -3.215*  (-1.82)      0.975   N=497
  Hedge funds     ERROR 'g1_conf' is not in list

## Financial center: index-relative return, Fin. center x Conf | Not fin. center x Conf | p(equal)
  Equity           -0.167   (-0.54)       -0.066   (-0.36)      0.805   N=801
  Fixed income     -0.343   (-0.61)        0.086   ( 0.29)      0.386   N=799
  Real estate      -0.880   (-0.89)       -0.297   (-0.65)      0.677   N=586
  Private equity   -7.731***(-5.85)       -3.577*  (-1.89)      0.174   N=497
  Hedge funds      -0.360   (-0.26)        0.682   ( 0.97)      0.575   N=271

## Prior private experience: index-relative return, Prior private x Conf | No prior private x Conf | p(equal)
  Equity            0.017   ( 0.10)       -0.376   (-1.33)      0.236   N=753
  Fixed income     -0.075   (-0.19)        0.444   ( 0.92)      0.417   N=751
  Real estate      -0.092   (-0.38)        0.179   ( 0.38)      0.576   N=556
  Private equity   -4.403** (-2.18)       -5.475   (-1.55)      0.794   N=488
  Hedge funds      -0.990   (-0.79)        3.568***( 4.51)      0.017   N=267