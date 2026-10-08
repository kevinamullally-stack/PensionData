# Time-to-departure / dose-response analysis
Sample: 2749 plan-years, 153 plans, 556 CIO-plan spells. Returns in percentage points.
Baseline controls: size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB + sib1 + cio_age + cio_tenure + prior_private_exp + Elite_inst | plan FE + year FE, SE clustered by plan.

## 0. Counts by departure type and years-to-departure bin
bin        m5  m4   m3   m2   m1   p0  na
dep_type                                 
censored  433  68   76   82   93  104   0
conf       63  34   59   69   70   48   0
other     274  95  123  140  155  103   1
unknown   248  48   57   65   83  158   0

Raw mean peer-adjusted return (pp) by bin:
           mean        count       
dep_type   conf  other  conf  other
bin                                
m5       -0.495  0.538  63.0  274.0
m4       -0.491  0.519  34.0   95.0
m3       -0.088  0.049  59.0  123.0
m2       -0.052 -0.613  69.0  140.0
m1        0.020 -0.283  70.0  155.0
p0        0.199 -0.519  48.0  103.0

Raw mean total fee pct (pp of assets) by bin:
           mean        count       
dep_type   conf  other  conf  other
bin                                
m5        0.227  0.296  57.0  192.0
m4        0.246  0.371  26.0   74.0
m3        0.275  0.384  49.0   99.0
m2        0.305  0.448  58.0  114.0
m1        0.301  0.444  58.0  129.0
p0        0.315  0.446  43.0   89.0

## 1. Baseline (reconstructed Table III spec)
ret100: Conflicted =  -0.469**  (0.203) p=0.022  N=2174
bret100: Conflicted =  -1.086*   (0.572) p=0.060  N=1559

## 2. Years-to-departure bins (reference: CIO-years with no observed departure)
### Pooled, plan+year FE: y=ret100, FE=ppd_id + fy, N=2174
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -1.202**  (0.504) p=0.018           0.077    (0.308) p=0.802          -1.279**  (0.563) p=0.025        
m4      -0.793*** (0.289) p=0.007           0.086    (0.347) p=0.805          -0.879**  (0.394) p=0.027        
m3      -0.628    (0.493) p=0.205          -0.237    (0.253) p=0.351          -0.391    (0.451) p=0.388        
m2      -0.657    (0.434) p=0.132          -0.451    (0.286) p=0.117          -0.206    (0.439) p=0.639        
m1      -0.360    (0.283) p=0.205          -0.564**  (0.253) p=0.027           0.204    (0.245) p=0.407        
p0      -0.545    (0.340) p=0.112          -0.442*   (0.243) p=0.071          -0.103    (0.287) p=0.721        
  Flatness test, conflicted bins all equal:            F=0.54 p=0.745
  Flatness test, other-departure bins all equal:       F=1.89 p=0.099
  Joint test conf profile == other profile (all bins): F=1.97 p=0.074
  Near(-2..0) minus Far(<=-4), conflicted:               0.477    (0.411) p=0.248
  Near minus Far, other departures:                     -0.567*** (0.215) p=0.009
  Diff-in-diff (conf near-far) - (other near-far):       1.044**  (0.456) p=0.024
  Near(-2,-1) minus Far, conflicted (excl. dep. year):   0.489    (0.404) p=0.229   DiD:   1.078**  (0.463) p=0.021

### Pooled, plan+year FE: y=bret100, FE=ppd_id + fy, N=1559
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -1.160*   (0.615) p=0.062          -0.375    (0.314) p=0.234          -0.784    (0.612) p=0.203        
m4      -1.462*** (0.467) p=0.002          -0.368    (0.312) p=0.240          -1.094**  (0.470) p=0.022        
m3      -2.364**  (1.077) p=0.030          -0.857*   (0.507) p=0.094          -1.507    (1.136) p=0.187        
m2      -1.226    (0.771) p=0.114          -0.282    (0.268) p=0.295          -0.945    (0.871) p=0.280        
m1      -1.030**  (0.464) p=0.028          -0.298    (0.280) p=0.289          -0.732    (0.470) p=0.122        
p0      -1.418*** (0.477) p=0.004          -0.174    (0.297) p=0.560          -1.244**  (0.500) p=0.014        
  Flatness test, conflicted bins all equal:            F=2.14 p=0.065
  Flatness test, other-departure bins all equal:       F=0.41 p=0.843
  Joint test conf profile == other profile (all bins): F=1.58 p=0.158
  Near(-2..0) minus Far(<=-4), conflicted:               0.086    (0.262) p=0.742
  Near minus Far, other departures:                      0.120    (0.248) p=0.629
  Diff-in-diff (conf near-far) - (other near-far):      -0.034    (0.354) p=0.923
  Near(-2,-1) minus Far, conflicted (excl. dep. year):   0.183    (0.266) p=0.494   DiD:   0.101    (0.397) p=0.799

### Within CIO-spell FE (profile identified within CIO): y=ret100, FE=spell + fy, N=2549  [coefficients relative to own <=-5 bin]
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m4       0.427    (0.455) p=0.350          -0.006    (0.363) p=0.988           0.433    (0.575) p=0.453        
m3       1.062    (0.835) p=0.206          -0.216    (0.277) p=0.438           1.277    (0.861) p=0.140        
m2       1.052    (0.676) p=0.122          -0.767**  (0.346) p=0.028           1.820**  (0.753) p=0.017        
m1       1.194*   (0.696) p=0.088          -0.399    (0.290) p=0.171           1.594**  (0.733) p=0.031        
p0       1.178    (0.766) p=0.126          -0.461    (0.392) p=0.242           1.638*   (0.847) p=0.055        
  Flatness test, conflicted bins all = far bin:        F=0.78 p=0.568
  Flatness test, other-departure bins all = far bin:   F=1.24 p=0.295
  Joint test conf profile == other profile:            F=1.80 p=0.116
  Near(-2..0) minus <=-5 bin, conflicted:                1.141*   (0.676) p=0.093   other:  -0.542*   (0.279) p=0.053   DiD:   1.684**  (0.717) p=0.020
  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:      0.928*   (0.511) p=0.071   other:  -0.540**  (0.264) p=0.043   DiD:   1.468*** (0.559) p=0.010

### Within CIO-spell FE (profile identified within CIO): y=bret100, FE=spell + fy, N=1795  [coefficients relative to own <=-5 bin]
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m4      -0.345    (0.581) p=0.554          -0.229    (0.321) p=0.476          -0.116    (0.631) p=0.855        
m3      -0.285    (0.780) p=0.716          -0.934    (0.669) p=0.165           0.650    (1.002) p=0.518        
m2       0.834    (0.569) p=0.145          -0.416    (0.370) p=0.264           1.250*   (0.699) p=0.076        
m1       0.962*   (0.575) p=0.097          -0.430    (0.337) p=0.204           1.392**  (0.690) p=0.046        
p0       0.490    (0.645) p=0.449          -0.085    (0.390) p=0.829           0.575    (0.674) p=0.396        
  Flatness test, conflicted bins all = far bin:        F=7.80 p=0.000
  Flatness test, other-departure bins all = far bin:   F=0.60 p=0.698
  Joint test conf profile == other profile:            F=2.30 p=0.049
  Near(-2..0) minus <=-5 bin, conflicted:                0.762    (0.546) p=0.165   other:  -0.310    (0.300) p=0.302   DiD:   1.072*   (0.611) p=0.082
  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:      0.934*** (0.308) p=0.003   other:  -0.196    (0.253) p=0.440   DiD:   1.130*** (0.412) p=0.007

## 3. Coarse bins: far (<=-4) / mid (-3,-2) / near (-1,0)
y=ret100 FE=ppd_id + fy N=2174
  far   conf  -1.047*** (0.360) p=0.004         other   0.068    (0.260) p=0.794         diff  -1.115*** (0.398) p=0.006
  mid   conf  -0.649    (0.424) p=0.128         other  -0.361    (0.237) p=0.131         diff  -0.288    (0.385) p=0.455
  near  conf  -0.439    (0.276) p=0.115         other  -0.539**  (0.227) p=0.019         diff   0.100    (0.209) p=0.632
  conf near-far   0.609    (0.459) p=0.187 | other near-far  -0.607*** (0.197) p=0.003 | DiD   1.216**  (0.493) p=0.015
y=ret100 FE=spell + fy N=2549  [relative to own far years]
  mid   conf   0.883    (0.598) p=0.142         other  -0.494**  (0.250) p=0.050         diff   1.376**  (0.634) p=0.032
  near  conf   1.018*   (0.556) p=0.069         other  -0.398*   (0.228) p=0.083         diff   1.416**  (0.579) p=0.016
  conf near-far   1.018*   (0.556) p=0.069 | other near-far  -0.398*   (0.228) p=0.083 | DiD   1.416**  (0.579) p=0.016
y=bret100 FE=ppd_id + fy N=1559
  far   conf  -1.301*** (0.489) p=0.009         other  -0.360    (0.279) p=0.200         diff  -0.940*   (0.485) p=0.055
  mid   conf  -1.737*   (0.889) p=0.053         other  -0.554*   (0.311) p=0.077         diff  -1.182    (0.949) p=0.215
  near  conf  -1.173*** (0.440) p=0.009         other  -0.262    (0.242) p=0.280         diff  -0.911**  (0.433) p=0.037
  conf near-far   0.127    (0.292) p=0.664 | other near-far   0.098    (0.246) p=0.691 | DiD   0.029    (0.370) p=0.938
y=bret100 FE=spell + fy N=1795  [relative to own far years]
  mid   conf   0.467    (0.432) p=0.282         other  -0.605    (0.430) p=0.162         diff   1.072*   (0.616) p=0.084
  near  conf   0.894**  (0.400) p=0.027         other  -0.292    (0.277) p=0.295         diff   1.186**  (0.493) p=0.018
  conf near-far   0.894**  (0.400) p=0.027 | other near-far  -0.292    (0.277) p=0.295 | DiD   1.186**  (0.493) p=0.018

## 4. Linear dose-response: y ~ Conf + Conf x YearsToDeparture + Other + Other x YearsToDeparture (ttd winsorized at -8; slope = change per year closer to exit)
y=ret100   FE=ppd_id + fy  N=2174: slope conf   0.122    (0.082) p=0.141 | slope other  -0.077*   (0.040) p=0.053 | diff   0.199**  (0.091) p=0.030  Conf level at exit yr  -0.370    (0.341) p=0.279
y=ret100   FE=spell + fy   N=2549: slope conf   0.160*   (0.092) p=0.084 | slope other  -0.077    (0.052) p=0.136 | diff   0.238**  (0.106) p=0.026
y=bret100  FE=ppd_id + fy  N=1559: slope conf   0.032    (0.068) p=0.638 | slope other   0.039    (0.051) p=0.440 | diff  -0.007    (0.083) p=0.930  Conf level at exit yr  -1.352**  (0.545) p=0.014
y=bret100  FE=spell + fy   N=1795: slope conf   0.162**  (0.078) p=0.041 | slope other  -0.000    (0.051) p=0.993 | diff   0.162*   (0.094) p=0.087
y=fee100   FE=ppd_id + fy  N=1873: slope conf  -0.004    (0.009) p=0.651 | slope other   0.010*   (0.006) p=0.068 | diff  -0.015    (0.010) p=0.152  Conf level at exit yr  -0.087    (0.070) p=0.213
y=fee100   FE=spell + fy   N=2123: slope conf   0.001    (0.010) p=0.901 | slope other  -0.002    (0.008) p=0.844 | diff   0.003    (0.011) p=0.790
y=expr100  FE=ppd_id + fy  N=2134: slope conf  -0.008    (0.012) p=0.497 | slope other   0.001    (0.005) p=0.834 | diff  -0.009    (0.013) p=0.478  Conf level at exit yr  -0.152**  (0.061) p=0.014
y=expr100  FE=spell + fy   N=2483: slope conf  -0.001    (0.011) p=0.921 | slope other  -0.005    (0.008) p=0.549 | diff   0.003    (0.012) p=0.773

## 5. First vs second half of tenure (departing spells only; second half = tenure > final tenure / 2)
Counts:
second_half  0.0  1.0
dep_type             
conf         149  164
other        392  462
y=ret100   FE=ppd_id + fy  N=953: 2nd-half effect conf  -0.007    (0.265) p=0.978 | other   0.049    (0.178) p=0.784 | diff  -0.056    (0.279) p=0.841 | conf 1st-half level  -0.196    (0.235) p=0.406
y=ret100   FE=spell + fy   N=1067: 2nd-half effect conf  -0.157    (0.250) p=0.533 | other  -0.551*   (0.302) p=0.071 | diff   0.395    (0.278) p=0.159
y=bret100  FE=ppd_id + fy  N=679: 2nd-half effect conf  -0.226    (0.336) p=0.504 | other   0.004    (0.378) p=0.993 | diff  -0.230    (0.451) p=0.612 | conf 1st-half level  -1.039**  (0.519) p=0.049
y=bret100  FE=spell + fy   N=754: 2nd-half effect conf  -0.494    (0.393) p=0.213 | other  -0.802*   (0.436) p=0.070 | diff   0.308    (0.357) p=0.391
y=fee100   FE=ppd_id + fy  N=795: 2nd-half effect conf   0.015    (0.025) p=0.536 | other   0.046**  (0.018) p=0.015 | diff  -0.030    (0.032) p=0.342 | conf 1st-half level  -0.187**  (0.078) p=0.018
y=fee100   FE=spell + fy   N=865: 2nd-half effect conf   0.011    (0.025) p=0.673 | other   0.006    (0.017) p=0.744 | diff   0.005    (0.033) p=0.876
y=expr100  FE=ppd_id + fy  N=940: 2nd-half effect conf   0.022    (0.026) p=0.401 | other   0.020    (0.017) p=0.245 | diff   0.002    (0.034) p=0.962 | conf 1st-half level  -0.169*** (0.058) p=0.005
y=expr100  FE=spell + fy   N=1054: 2nd-half effect conf   0.022    (0.024) p=0.376 | other   0.023    (0.017) p=0.183 | diff  -0.001    (0.031) p=0.966
  (robustness: second half defined with >=)
y=ret100   pooled N=953: conf   0.248    (0.280) p=0.378 | other   0.099    (0.164) p=0.548 | diff   0.149    (0.307) p=0.629
y=bret100  pooled N=679: conf  -0.160    (0.344) p=0.643 | other   0.321    (0.284) p=0.263 | diff  -0.480    (0.466) p=0.307

## 6. Fee and allocation profiles by years-to-departure bin (pooled plan+year FE, baseline controls)
### Pooled: y=fee100, FE=ppd_id + fy, N=1873
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.042    (0.081) p=0.603           0.006    (0.042) p=0.891          -0.048    (0.076) p=0.525        
m4      -0.063    (0.075) p=0.400           0.048    (0.035) p=0.178          -0.111    (0.074) p=0.139        
m3      -0.107    (0.064) p=0.100           0.030    (0.031) p=0.332          -0.137**  (0.063) p=0.032        
m2      -0.082    (0.070) p=0.242           0.071*   (0.040) p=0.077          -0.153**  (0.074) p=0.041        
m1      -0.084    (0.070) p=0.235           0.060    (0.037) p=0.102          -0.144*   (0.073) p=0.050        
p0      -0.075    (0.073) p=0.312           0.078**  (0.035) p=0.029          -0.152**  (0.075) p=0.046        
  Flatness test, conflicted bins all equal:            F=0.79 p=0.556
  Flatness test, other-departure bins all equal:       F=1.70 p=0.140
  Joint test conf profile == other profile (all bins): F=1.39 p=0.222
  Near(-2..0) minus Far(<=-4), conflicted:              -0.027    (0.046) p=0.552
  Near minus Far, other departures:                      0.043*   (0.026) p=0.100
  Diff-in-diff (conf near-far) - (other near-far):      -0.070    (0.050) p=0.165
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.030    (0.044) p=0.497   DiD:  -0.069    (0.050) p=0.169

### Pooled: y=expr100, FE=ppd_id + fy, N=2134
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.094    (0.074) p=0.208          -0.016    (0.035) p=0.654          -0.078    (0.070) p=0.266        
m4      -0.132**  (0.061) p=0.032          -0.010    (0.029) p=0.740          -0.122**  (0.055) p=0.028        
m3      -0.147*** (0.051) p=0.004          -0.049    (0.032) p=0.128          -0.098*** (0.037) p=0.008        
m2      -0.152*** (0.054) p=0.005           0.009    (0.030) p=0.766          -0.161*** (0.055) p=0.004        
m1      -0.132**  (0.054) p=0.017          -0.013    (0.031) p=0.673          -0.119**  (0.057) p=0.039        
p0      -0.142**  (0.067) p=0.035          -0.001    (0.037) p=0.985          -0.142*   (0.075) p=0.061        
  Flatness test, conflicted bins all equal:            F=1.13 p=0.349
  Flatness test, other-departure bins all equal:       F=1.71 p=0.137
  Joint test conf profile == other profile (all bins): F=2.86 p=0.012
  Near(-2..0) minus Far(<=-4), conflicted:              -0.029    (0.043) p=0.499
  Near minus Far, other departures:                      0.011    (0.020) p=0.586
  Diff-in-diff (conf near-far) - (other near-far):      -0.040    (0.048) p=0.399
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.029    (0.042) p=0.487   DiD:  -0.040    (0.045) p=0.380

### Pooled: y=pefee100, FE=ppd_id + fy, N=1700
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.146    (0.349) p=0.676           0.405    (0.247) p=0.105          -0.551    (0.421) p=0.193        
m4      -0.557    (0.344) p=0.108           0.113    (0.254) p=0.658          -0.670    (0.430) p=0.122        
m3      -0.914*** (0.282) p=0.002          -0.019    (0.244) p=0.937          -0.894**  (0.400) p=0.027        
m2      -0.850*** (0.298) p=0.005           0.059    (0.268) p=0.825          -0.909**  (0.439) p=0.041        
m1      -0.912*** (0.314) p=0.004          -0.052    (0.194) p=0.790          -0.860**  (0.362) p=0.019        
p0      -0.747**  (0.341) p=0.030           0.212    (0.215) p=0.326          -0.960**  (0.390) p=0.015        
  Flatness test, conflicted bins all equal:            F=2.95 p=0.015
  Flatness test, other-departure bins all equal:       F=2.06 p=0.075
  Joint test conf profile == other profile (all bins): F=1.39 p=0.225
  Near(-2..0) minus Far(<=-4), conflicted:              -0.485**  (0.221) p=0.030
  Near minus Far, other departures:                     -0.185    (0.192) p=0.336
  Diff-in-diff (conf near-far) - (other near-far):      -0.300    (0.275) p=0.277
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.530**  (0.233) p=0.025   DiD:  -0.275    (0.282) p=0.332

### Pooled: y=refee100, FE=ppd_id + fy, N=1711
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.441*   (0.250) p=0.080           0.072    (0.164) p=0.663          -0.512*   (0.262) p=0.053        
m4      -0.459*   (0.267) p=0.088          -0.108    (0.134) p=0.422          -0.351    (0.275) p=0.204        
m3      -0.538**  (0.214) p=0.013          -0.098    (0.120) p=0.413          -0.440**  (0.202) p=0.032        
m2      -0.590**  (0.232) p=0.012           0.038    (0.132) p=0.777          -0.627**  (0.250) p=0.013        
m1      -0.528**  (0.245) p=0.033           0.076    (0.142) p=0.594          -0.604**  (0.281) p=0.033        
p0      -0.344    (0.251) p=0.174           0.146    (0.170) p=0.391          -0.490    (0.329) p=0.139        
  Flatness test, conflicted bins all equal:            F=0.71 p=0.613
  Flatness test, other-departure bins all equal:       F=1.24 p=0.293
  Joint test conf profile == other profile (all bins): F=1.38 p=0.228
  Near(-2..0) minus Far(<=-4), conflicted:              -0.038    (0.125) p=0.765
  Near minus Far, other departures:                      0.105    (0.121) p=0.390
  Diff-in-diff (conf near-far) - (other near-far):      -0.142    (0.159) p=0.374
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.109    (0.145) p=0.451   DiD:  -0.184    (0.175) p=0.294

### Pooled: y=hffee100, FE=ppd_id + fy, N=1910
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5       0.207    (0.194) p=0.288           0.212    (0.165) p=0.200          -0.005    (0.196) p=0.980        
m4      -0.074    (0.207) p=0.720           0.908    (0.750) p=0.228          -0.983    (0.716) p=0.172        
m3      -0.128    (0.167) p=0.445           0.194    (0.118) p=0.104          -0.321**  (0.162) p=0.049        
m2      -0.076    (0.192) p=0.692           0.189    (0.123) p=0.126          -0.265    (0.205) p=0.197        
m1      -0.076    (0.180) p=0.675           0.322**  (0.155) p=0.040          -0.398*   (0.235) p=0.093        
p0       0.093    (0.237) p=0.694           0.642*** (0.208) p=0.002          -0.549*   (0.300) p=0.070        
  Flatness test, conflicted bins all equal:            F=1.30 p=0.266
  Flatness test, other-departure bins all equal:       F=2.24 p=0.054
  Joint test conf profile == other profile (all bins): F=1.25 p=0.287
  Near(-2..0) minus Far(<=-4), conflicted:              -0.086    (0.158) p=0.588
  Near minus Far, other departures:                     -0.176    (0.372) p=0.637
  Diff-in-diff (conf near-far) - (other near-far):       0.090    (0.406) p=0.825
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.142    (0.134) p=0.292   DiD:   0.162    (0.408) p=0.691

### Pooled: y=eqfee100, FE=ppd_id + fy, N=1604
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5       0.085*   (0.043) p=0.052           0.008    (0.025) p=0.758           0.077**  (0.033) p=0.020        
m4       0.046    (0.033) p=0.173           0.000    (0.020) p=0.982           0.045*   (0.026) p=0.087        
m3       0.005    (0.032) p=0.870           0.010    (0.016) p=0.533          -0.005    (0.027) p=0.863        
m2       0.006    (0.030) p=0.841          -0.001    (0.018) p=0.940           0.007    (0.025) p=0.768        
m1      -0.004    (0.030) p=0.886           0.006    (0.020) p=0.767          -0.010    (0.024) p=0.671        
p0      -0.025    (0.030) p=0.398           0.057    (0.041) p=0.174          -0.082**  (0.039) p=0.040        
  Flatness test, conflicted bins all equal:            F=2.17 p=0.062
  Flatness test, other-departure bins all equal:       F=0.94 p=0.459
  Joint test conf profile == other profile (all bins): F=3.01 p=0.009
  Near(-2..0) minus Far(<=-4), conflicted:              -0.073*** (0.026) p=0.006
  Near minus Far, other departures:                      0.016    (0.019) p=0.393
  Diff-in-diff (conf near-far) - (other near-far):      -0.089*** (0.025) p=0.001
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.064**  (0.025) p=0.011   DiD:  -0.063**  (0.024) p=0.011

### Pooled: y=fifee100, FE=ppd_id + fy, N=1604
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.045    (0.046) p=0.335          -0.012    (0.048) p=0.799          -0.033    (0.037) p=0.374        
m4      -0.062    (0.041) p=0.136           0.050    (0.030) p=0.101          -0.112**  (0.045) p=0.014        
m3      -0.053    (0.037) p=0.149           0.012    (0.029) p=0.681          -0.065**  (0.027) p=0.018        
m2      -0.025    (0.043) p=0.571           0.058*   (0.032) p=0.072          -0.083**  (0.040) p=0.042        
m1      -0.013    (0.049) p=0.789           0.055    (0.038) p=0.156          -0.068    (0.047) p=0.151        
p0       0.001    (0.036) p=0.989          -0.000    (0.040) p=0.991           0.001    (0.031) p=0.975        
  Flatness test, conflicted bins all equal:            F=1.37 p=0.241
  Flatness test, other-departure bins all equal:       F=1.59 p=0.169
  Joint test conf profile == other profile (all bins): F=1.73 p=0.120
  Near(-2..0) minus Far(<=-4), conflicted:               0.041    (0.027) p=0.132
  Near minus Far, other departures:                      0.019    (0.019) p=0.336
  Diff-in-diff (conf near-far) - (other near-far):       0.022    (0.028) p=0.421
  Near(-2,-1) minus Far, conflicted (excl. dep. year):   0.035    (0.035) p=0.324   DiD:  -0.003    (0.041) p=0.939

### Pooled: y=total_fee_rank, FE=ppd_id + fy, N=1873
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5       0.190    (0.179) p=0.290           0.036    (0.110) p=0.745           0.155    (0.189) p=0.416        
m4       0.101    (0.157) p=0.521           0.026    (0.111) p=0.816           0.075    (0.176) p=0.671        
m3       0.250**  (0.119) p=0.037           0.091    (0.087) p=0.297           0.159    (0.120) p=0.187        
m2       0.205**  (0.103) p=0.049           0.072    (0.089) p=0.419           0.132    (0.105) p=0.208        
m1       0.228*   (0.124) p=0.069           0.047    (0.075) p=0.533           0.181    (0.124) p=0.149        
p0       0.085    (0.166) p=0.611           0.042    (0.087) p=0.634           0.043    (0.175) p=0.806        
  Flatness test, conflicted bins all equal:            F=0.52 p=0.759
  Flatness test, other-departure bins all equal:       F=0.29 p=0.917
  Joint test conf profile == other profile (all bins): F=0.77 p=0.598
  Near(-2..0) minus Far(<=-4), conflicted:               0.027    (0.125) p=0.830
  Near minus Far, other departures:                      0.023    (0.065) p=0.725
  Diff-in-diff (conf near-far) - (other near-far):       0.004    (0.142) p=0.978
  Near(-2,-1) minus Far, conflicted (excl. dep. year):   0.071    (0.110) p=0.523   DiD:   0.042    (0.127) p=0.743

### Pooled: y=alt_actl, FE=ppd_id + fy, N=2137
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.067**  (0.026) p=0.010          -0.040**  (0.016) p=0.014          -0.027    (0.024) p=0.275        
m4      -0.022    (0.023) p=0.339          -0.037*** (0.012) p=0.003           0.015    (0.022) p=0.484        
m3      -0.035*   (0.020) p=0.075          -0.028**  (0.012) p=0.027          -0.007    (0.015) p=0.642        
m2      -0.040**  (0.018) p=0.030          -0.039*** (0.013) p=0.003          -0.001    (0.013) p=0.932        
m1      -0.033*   (0.020) p=0.095          -0.027**  (0.013) p=0.039          -0.007    (0.014) p=0.645        
p0      -0.015    (0.017) p=0.381          -0.027**  (0.013) p=0.046           0.012    (0.013) p=0.360        
  Flatness test, conflicted bins all equal:            F=3.53 p=0.005
  Flatness test, other-departure bins all equal:       F=3.52 p=0.005
  Joint test conf profile == other profile (all bins): F=1.75 p=0.114
  Near(-2..0) minus Far(<=-4), conflicted:               0.015    (0.018) p=0.403
  Near minus Far, other departures:                      0.008    (0.009) p=0.386
  Diff-in-diff (conf near-far) - (other near-far):       0.007    (0.019) p=0.699
  Near(-2,-1) minus Far, conflicted (excl. dep. year):   0.008    (0.017) p=0.663   DiD:   0.002    (0.018) p=0.919

### Pooled: y=PETotal_Actl, FE=ppd_id + fy, N=2137
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m5      -0.022*   (0.011) p=0.052          -0.027*** (0.007) p=0.000           0.005    (0.012) p=0.679        
m4      -0.002    (0.009) p=0.828          -0.025*** (0.005) p=0.000           0.023**  (0.009) p=0.011        
m3      -0.013*   (0.008) p=0.097          -0.020*** (0.005) p=0.000           0.007    (0.007) p=0.276        
m2      -0.014*   (0.008) p=0.079          -0.020*** (0.005) p=0.000           0.007    (0.006) p=0.268        
m1      -0.013*   (0.008) p=0.095          -0.017*** (0.005) p=0.002           0.005    (0.006) p=0.429        
p0      -0.013    (0.008) p=0.106          -0.015**  (0.006) p=0.013           0.002    (0.007) p=0.792        
  Flatness test, conflicted bins all equal:            F=2.31 p=0.047
  Flatness test, other-departure bins all equal:       F=1.39 p=0.233
  Joint test conf profile == other profile (all bins): F=2.51 p=0.025
  Near(-2..0) minus Far(<=-4), conflicted:              -0.001    (0.008) p=0.886
  Near minus Far, other departures:                      0.008**  (0.004) p=0.041
  Diff-in-diff (conf near-far) - (other near-far):      -0.010    (0.009) p=0.285
  Near(-2,-1) minus Far, conflicted (excl. dep. year):  -0.001    (0.008) p=0.876   DiD:  -0.008    (0.009) p=0.329

## 6b. Fee profiles within CIO-spell
### Within spell: y=fee100, FE=spell + fy, N=2123  [coefficients relative to own <=-5 bin]
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m4      -0.052    (0.051) p=0.315          -0.012    (0.034) p=0.719          -0.040    (0.058) p=0.498        
m3      -0.069    (0.046) p=0.137          -0.045    (0.032) p=0.168          -0.024    (0.051) p=0.630        
m2      -0.035    (0.048) p=0.468          -0.016    (0.035) p=0.654          -0.019    (0.052) p=0.717        
m1      -0.040    (0.052) p=0.437          -0.019    (0.036) p=0.593          -0.021    (0.054) p=0.697        
p0      -0.037    (0.060) p=0.545          -0.043    (0.040) p=0.290           0.006    (0.060) p=0.919        
  Flatness test, conflicted bins all = far bin:        F=1.05 p=0.392
  Flatness test, other-departure bins all = far bin:   F=1.54 p=0.181
  Joint test conf profile == other profile:            F=0.33 p=0.897
  Near(-2..0) minus <=-5 bin, conflicted:               -0.037    (0.052) p=0.476   other:  -0.026    (0.035) p=0.463   DiD:  -0.011    (0.053) p=0.832
  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:     -0.011    (0.049) p=0.820   other:  -0.020    (0.029) p=0.495   DiD:   0.009    (0.052) p=0.869

### Within spell: y=expr100, FE=spell + fy, N=2483  [coefficients relative to own <=-5 bin]
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m4      -0.020    (0.046) p=0.665          -0.017    (0.026) p=0.512          -0.003    (0.051) p=0.956        
m3      -0.008    (0.054) p=0.879          -0.054*   (0.031) p=0.083           0.046    (0.059) p=0.438        
m2      -0.031    (0.057) p=0.586          -0.005    (0.033) p=0.874          -0.026    (0.061) p=0.672        
m1      -0.013    (0.058) p=0.823          -0.010    (0.036) p=0.791          -0.003    (0.061) p=0.957        
p0      -0.011    (0.065) p=0.865          -0.042    (0.039) p=0.282           0.031    (0.068) p=0.651        
  Flatness test, conflicted bins all = far bin:        F=1.42 p=0.219
  Flatness test, other-departure bins all = far bin:   F=1.61 p=0.159
  Joint test conf profile == other profile:            F=1.92 p=0.094
  Near(-2..0) minus <=-5 bin, conflicted:               -0.018    (0.059) p=0.757   other:  -0.019    (0.034) p=0.580   DiD:   0.000    (0.062) p=0.994
  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:     -0.008    (0.043) p=0.846   other:  -0.010    (0.024) p=0.668   DiD:   0.002    (0.044) p=0.966

### Within spell: y=pefee100, FE=spell + fy, N=1942  [coefficients relative to own <=-5 bin]
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m4      -0.179    (0.169) p=0.292          -0.295**  (0.148) p=0.048           0.116    (0.203) p=0.569        
m3      -0.430**  (0.175) p=0.015          -0.490*** (0.160) p=0.003           0.060    (0.192) p=0.757        
m2      -0.297    (0.196) p=0.131          -0.404**  (0.188) p=0.034           0.107    (0.214) p=0.620        
m1      -0.366*   (0.217) p=0.094          -0.441**  (0.214) p=0.042           0.075    (0.227) p=0.740        
p0      -0.367    (0.253) p=0.149          -0.274    (0.277) p=0.324          -0.093    (0.299) p=0.756        
  Flatness test, conflicted bins all = far bin:        F=1.43 p=0.216
  Flatness test, other-departure bins all = far bin:   F=2.01 p=0.082
  Joint test conf profile == other profile:            F=0.32 p=0.902
  Near(-2..0) minus <=-5 bin, conflicted:               -0.343    (0.213) p=0.109   other:  -0.373*   (0.199) p=0.063   DiD:   0.030    (0.216) p=0.891
  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:     -0.254    (0.220) p=0.250   other:  -0.226    (0.186) p=0.226   DiD:  -0.028    (0.240) p=0.906

### Within spell: y=alt_actl, FE=spell + fy, N=2463  [coefficients relative to own <=-5 bin]
bin    Conflicted x bin                   Other-departure x bin              Difference (conf - other)         
m4       0.044**  (0.017) p=0.010           0.007    (0.008) p=0.379           0.037*   (0.019) p=0.054        
m3       0.057*** (0.019) p=0.003           0.013    (0.009) p=0.187           0.045**  (0.021) p=0.034        
m2       0.052**  (0.022) p=0.019           0.007    (0.010) p=0.493           0.045*   (0.023) p=0.059        
m1       0.057**  (0.026) p=0.029           0.020*   (0.011) p=0.069           0.037    (0.027) p=0.176        
p0       0.068**  (0.027) p=0.014           0.016    (0.013) p=0.221           0.051*   (0.029) p=0.081        
  Flatness test, conflicted bins all = far bin:        F=2.54 p=0.031
  Flatness test, other-departure bins all = far bin:   F=3.33 p=0.007
  Joint test conf profile == other profile:            F=1.73 p=0.132
  Near(-2..0) minus <=-5 bin, conflicted:                0.059**  (0.025) p=0.018   other:   0.014    (0.011) p=0.191   DiD:   0.044*   (0.026) p=0.091
  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:      0.037*   (0.020) p=0.064   other:   0.011    (0.008) p=0.192   DiD:   0.026    (0.021) p=0.214

## 6c. Robustness of the returns profile (coarse bins, pooled)
(a) tenure bins instead of linear tenure, y=ret100 N=2174: conf far  -1.036*** (0.364) p=0.005 near  -0.462    (0.290) p=0.113 near-far   0.574    (0.447) p=0.202 | DiD   1.224**  (0.484) p=0.013
(b) drop unknown-exit spells, y=ret100 N=1709: conf far  -0.853**  (0.330) p=0.011 near  -0.429    (0.307) p=0.165 near-far   0.424    (0.432) p=0.328 | DiD   0.977**  (0.485) p=0.046
(c) departing spells only (ref = other far), y=ret100 N=974: conf far  -0.520    (0.455) p=0.256 near  -0.395    (0.258) p=0.129 near-far   0.125    (0.466) p=0.789 | DiD   0.751    (0.492) p=0.130
(d) conflicted spells with final tenure >= 4 only (same CIOs in far & near), y=ret100 N=2078: conf far  -1.150*** (0.403) p=0.005 near  -0.262    (0.333) p=0.433 near-far   0.888    (0.587) p=0.133 | DiD   1.489**  (0.617) p=0.017
(a) tenure bins instead of linear tenure, y=bret100 N=1559: conf far  -1.270*** (0.485) p=0.010 near  -1.184**  (0.459) p=0.011 near-far   0.086    (0.296) p=0.773 | DiD   0.009    (0.368) p=0.981
(b) drop unknown-exit spells, y=bret100 N=1206: conf far  -1.138**  (0.434) p=0.010 near  -1.065**  (0.508) p=0.038 near-far   0.073    (0.287) p=0.800 | DiD   0.012    (0.369) p=0.973
(c) departing spells only (ref = other far), y=bret100 N=690: conf far  -0.807*   (0.479) p=0.097 near  -0.980**  (0.444) p=0.031 near-far  -0.173    (0.361) p=0.633 | DiD   0.066    (0.413) p=0.874
(d) conflicted spells with final tenure >= 4 only (same CIOs in far & near), y=bret100 N=1497: conf far  -1.625**  (0.691) p=0.020 near  -1.331**  (0.575) p=0.022 near-far   0.295    (0.411) p=0.475 | DiD   0.223    (0.464) p=0.632

## 6d. Authors' own close_conf / far_conf split, for reference
y=ret100   N=2174: close  -0.349    (0.211) p=0.101 | far  -1.195*** (0.451) p=0.009 | close-far   0.845*   (0.456) p=0.066
y=bret100  N=1559: close  -1.130*   (0.594) p=0.060 | far  -0.737    (0.446) p=0.101 | close-far  -0.393    (0.380) p=0.303
y=fee100   N=1873: close  -0.127*   (0.066) p=0.055 | far  -0.032    (0.069) p=0.641 | close-far  -0.095**  (0.047) p=0.045
y=expr100  N=2134: close  -0.138*** (0.050) p=0.007 | far  -0.046    (0.064) p=0.474 | close-far  -0.092    (0.059) p=0.120

## 7. Mediation: does controlling for fees absorb the conflicted / near-departure effect?
y=ret100: same sample N=1873: Conf no fee ctrl  -0.425**  (0.187) p=0.024 | with fee level  -0.488**  (0.192) p=0.012 (fee coef  -0.541**  (0.264) p=0.043) | with authors' Fee Slope var (N=1835)  -0.512*** (0.183) p=0.006
   near-departure conf effect: no fee ctrl  -0.643**  (0.298) p=0.033 | with fee ctrl  -0.679**  (0.288) p=0.020
y=bret100: same sample N=1422: Conf no fee ctrl  -0.450    (0.316) p=0.156 | with fee level  -0.445    (0.320) p=0.167 (fee coef   0.696*** (0.259) p=0.008) | with authors' Fee Slope var (N=1402)  -0.501    (0.311) p=0.110
   near-departure conf effect: no fee ctrl  -1.070*** (0.377) p=0.005 | with fee ctrl  -1.113*** (0.389) p=0.005

## 8. Near-minus-far profile by departure type (pooled plan+year FE). Types among non-conflicted observed departures.
bin         m5   m4   m3   m2   m1   p0  na
typ                                        
conf        63   34   59   69   70   48   0
none       722  136  156  175  204  280   1
privnonam   28    6   11   17   25    8   0
public      88   35   52   61   68   44   0
retire     117   34   37   34   34   33   0
y=ret100 N=2174
  conf       far  -1.056*** (0.358) p=0.004     near  -0.392    (0.238) p=0.101     near-far   0.664    (0.458) p=0.149    
  retire     far   0.159    (0.425) p=0.708     near  -0.397    (0.295) p=0.181     near-far  -0.556*   (0.327) p=0.091     conf minus this type   1.221**  (0.568) p=0.033
  public     far  -0.078    (0.262) p=0.765     near  -0.643*** (0.235) p=0.007     near-far  -0.565**  (0.228) p=0.015     conf minus this type   1.229**  (0.501) p=0.015
  privnonam  far   0.064    (0.828) p=0.938     near  -1.001**  (0.424) p=0.020     near-far  -1.065    (0.841) p=0.208     conf minus this type   1.730*   (0.937) p=0.067
y=bret100 N=1559
  conf       far  -1.409**  (0.584) p=0.017     near  -1.205**  (0.505) p=0.019     near-far   0.204    (0.289) p=0.482    
  retire     far  -0.379    (0.468) p=0.419     near   0.551    (0.445) p=0.218     near-far   0.930**  (0.429) p=0.032     conf minus this type  -0.726    (0.612) p=0.238
  public     far  -0.529    (0.361) p=0.145     near  -0.798**  (0.367) p=0.032     near-far  -0.268    (0.283) p=0.345     conf minus this type   0.472    (0.379) p=0.215
  privnonam  far   0.084    (1.814) p=0.963     near  -1.320    (0.802) p=0.102     near-far  -1.404    (1.994) p=0.483     conf minus this type   1.608    (1.979) p=0.418
y=fee100 N=1873
  conf       far  -0.063    (0.075) p=0.400     near  -0.099    (0.071) p=0.164     near-far  -0.036    (0.048) p=0.459    
  retire     far   0.029    (0.052) p=0.570     near   0.021    (0.049) p=0.671     near-far  -0.009    (0.044) p=0.845     conf minus this type  -0.027    (0.062) p=0.660
  public     far   0.001    (0.045) p=0.974     near   0.040    (0.040) p=0.325     near-far   0.038    (0.034) p=0.265     conf minus this type  -0.074    (0.057) p=0.192
  privnonam  far   0.033    (0.074) p=0.651     near   0.091    (0.059) p=0.123     near-far   0.058    (0.085) p=0.499     conf minus this type  -0.094    (0.092) p=0.310

