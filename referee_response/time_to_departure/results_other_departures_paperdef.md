# Other-departure comparison, paper definitions: Conflicted = conf_pen_vendor, sample cio_dum==1 & fy<=2020 & curr1==0, do-file controls, SE double clustered by plan and year (t-stats in parentheses)

Halves sample: 1261 CIO-years | conflicted CIOs 45 (356 yrs) | other classified departures 145 CIOs (905 yrs)
other departure types (CIO-years, non-exclusive): retire 604 | leave public 280 | private non-vendor 22 | die 8

## 1. Second half minus first half: conflicted vs other departures (reference = first half of each group; 'Conflicted' row = conflicted first-half level vs other departers' first half)

### Peer-adjusted return
spec                           Conf level (1st half)    Conf 2nd-1st             Other 2nd-1st            Difference               N
(1) Year FE, base controls      -0.769***(-3.86)         -0.065   (-0.28)         -0.312   (-1.17)          0.248   ( 0.90)        1121
(2) Year FE, all controls       -0.702** (-2.39)         -0.059   (-0.26)         -0.406*  (-1.88)          0.346   ( 1.03)        1000
(4) Plan + Year FE              -0.225   (-0.55)          0.280   ( 1.14)         -0.488** (-2.17)          0.768*  ( 1.87)        996
(5) CIO FE + Year FE              absorbed               -0.116   (-0.37)         -1.143***(-3.37)          1.027***( 2.93)        1027
(4) vs ALL non-conf departers   -0.802*  (-2.03)          0.382   ( 1.61)         -0.182   (-1.20)          0.564   ( 1.61)        1188

### Benchmark-adjusted return
spec                           Conf level (1st half)    Conf 2nd-1st             Other 2nd-1st            Difference               N
(1) Year FE, base controls      -0.294   (-1.06)         -1.191*  (-1.92)         -0.361   (-1.28)         -0.830   (-1.28)        861
(2) Year FE, all controls       -0.294   (-0.87)         -0.958** (-2.17)         -0.590** (-2.17)         -0.367   (-0.66)        768
(4) Plan + Year FE              -0.149   (-0.23)         -1.143** (-2.18)         -0.688** (-2.38)         -0.455   (-0.76)        762
(5) CIO FE + Year FE              absorbed               -1.898*  (-1.86)         -1.156***(-3.44)         -0.743   (-0.83)        798
(4) vs ALL non-conf departers   -0.386   (-0.65)         -1.071*  (-2.08)         -0.491*  (-1.93)         -0.580   (-1.00)        876

### Fee ratio
spec                           Conf level (1st half)    Conf 2nd-1st             Other 2nd-1st            Difference               N
(1) Year FE, base controls      -0.048   (-1.56)         -0.013   (-0.34)          0.006   ( 0.25)         -0.018   (-0.48)        973
(2) Year FE, all controls        0.021   ( 0.42)         -0.019   (-0.47)          0.013   ( 0.56)         -0.033   (-0.73)        880
(4) Plan + Year FE              -0.038   (-0.63)         -0.027   (-0.65)          0.018   ( 0.78)         -0.044   (-0.99)        875
(5) CIO FE + Year FE              absorbed               -0.034   (-0.85)         -0.038   (-1.37)          0.004   ( 0.09)        886
(4) vs ALL non-conf departers    0.022   ( 0.39)         -0.030   (-0.76)         -0.004   (-0.19)         -0.026   (-0.64)        1020

## 2. Years-to-departure bins. Pooled: reference = non-departing CIO-years in the curr1==0 sample (long-tenured current CIOs) and unclassified exits. Within CIO: relative to own <=-5 years.

### Peer-adjusted return | Pooled, plan + year FE | N=1482
bin    Conflicted               Other departure          Difference              
m5      -1.353** (-2.23)         -0.264   (-0.74)         -1.089   (-1.60)       
m4      -1.037** (-2.14)         -0.305   (-1.17)         -0.732   (-1.13)       
m3      -0.923** (-2.26)         -0.161   (-0.62)         -0.762*  (-1.75)       
m2      -1.273** (-2.79)         -0.516   (-1.61)         -0.757** (-2.11)       
m1      -0.634*  (-1.91)         -0.333   (-1.24)         -0.301   (-0.69)       
p0      -0.832** (-2.29)         -0.630*  (-1.91)         -0.201   (-0.63)       
  Near(-2..0) - Far(<=-4): conflicted   0.282   ( 0.58) | other  -0.208   (-1.04) | DiD   0.490   ( 0.91)

### Peer-adjusted return | Within CIO, CIO + year FE | N=1587  [relative to own <=-5 bin]
bin    Conflicted               Other departure          Difference              
m4       0.283   ( 0.52)         -0.150   (-0.71)          0.433   ( 0.73)       
m3       0.432   ( 0.54)         -0.078   (-0.30)          0.510   ( 0.62)       
m2       0.051   ( 0.07)         -0.543   (-1.69)          0.594   ( 0.72)       
m1       0.738   ( 1.15)         -0.421   (-1.39)          1.159*  ( 1.86)       
p0       0.587   ( 0.72)         -0.728*  (-1.91)          1.315   ( 1.54)       
  Near(-2..0) - Far(<=-4): conflicted   0.317   ( 0.55) | other  -0.489** (-2.54) | DiD   0.806   ( 1.35)

### Benchmark-adjusted return | Pooled, plan + year FE | N=1069
bin    Conflicted               Other departure          Difference              
m5       0.011   ( 0.01)         -0.042   (-0.09)          0.053   ( 0.04)       
m4      -0.990   (-1.43)         -0.343   (-0.97)         -0.646   (-0.88)       
m3      -2.422** (-2.41)         -0.121   (-0.44)         -2.301** (-2.47)       
m2      -0.657   (-1.05)         -0.075   (-0.16)         -0.581   (-0.79)       
m1      -0.715   (-1.44)         -0.340   (-1.20)         -0.375   (-0.72)       
p0      -1.321** (-2.44)         -0.053   (-0.19)         -1.267*  (-1.90)       
  Near(-2..0) - Far(<=-4): conflicted  -0.408   (-0.62) | other   0.037   ( 0.17) | DiD  -0.445   (-0.62)

### Benchmark-adjusted return | Within CIO, CIO + year FE | N=1146  [relative to own <=-5 bin]
bin    Conflicted               Other departure          Difference              
m4      -1.066   (-1.45)         -0.320   (-0.97)         -0.746   (-0.88)       
m3      -3.438   (-1.23)         -0.169   (-0.38)         -3.269   (-1.12)       
m2      -1.284   (-0.94)         -0.143   (-0.36)         -1.141   (-0.82)       
m1      -0.982   (-0.87)         -0.654   (-1.57)         -0.328   (-0.27)       
p0      -2.153   (-1.46)         -0.049   (-0.08)         -2.104   (-1.24)       
  Near(-2..0) - Far(<=-4): conflicted  -0.940   (-0.98) | other  -0.122   (-0.35) | DiD  -0.818   (-0.82)

## 3. Near (-1,0) minus far (<=-4) by departure type, pooled plan + year FE, all controls, peer-adjusted

Peer-adjusted N=1482: counts {'conf': 364, 'retire': 620, 'public': 279, 'privnonam': 29}
  conf       far  -1.238** (-2.61)      near  -0.726** (-2.23)      near-far   0.512   ( 1.01)     
  retire     far  -0.523   (-1.30)      near  -0.479   (-1.46)      near-far   0.044   ( 0.13)      conf minus retire:   0.468   ( 0.85)
  public     far   0.239   ( 0.57)      near  -0.652*  (-1.75)      near-far  -0.891** (-2.62)      conf minus public:   1.403** ( 2.19)
  privnonam  far   0.052   ( 0.10)      near   0.338   ( 1.02)      near-far   0.286   ( 0.70)      conf minus privnonam:   0.226   ( 0.37)

Benchmark-adjusted N=1069: counts {'conf': 364, 'retire': 620, 'public': 279, 'privnonam': 29}
  conf       far  -0.551   (-0.76)      near  -0.958** (-2.28)      near-far  -0.407   (-0.73)     
  retire     far  -0.333   (-0.69)      near  -0.075   (-0.25)      near-far   0.258   ( 0.79)      conf minus retire:  -0.665   (-0.97)
  public     far   0.147   ( 0.40)      near  -0.525** (-2.64)      near-far  -0.672*  (-1.94)      conf minus public:   0.265   ( 0.36)
  privnonam  far  -1.163** (-2.28)      near  -0.112   (-0.18)      near-far   1.051*  ( 1.75)      conf minus privnonam:  -1.458*  (-1.94)