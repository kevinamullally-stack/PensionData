
# COMMON SAMPLE (both peer- and benchmark-adjusted returns non-missing). Paper spec; SE double clustered by plan & year; t in parentheses.

## A. Table III baseline, Conflicted CIO coefficient, common sample
  Peer-adj   (1) Year FE, base:  -0.614***(-3.07) N=1240 | (2) Year FE, all:  -0.584** (-2.37) N=1072 | (3) Plan FE:  -0.440   (-1.11) N=1069 | (4) Plan+Year FE:  -0.498   (-1.28) N=1069
  Bench-adj  (1) Year FE, base:  -0.518** (-2.65) N=1240 | (2) Year FE, all:  -0.598***(-3.19) N=1072 | (3) Plan FE:  -0.959** (-2.23) N=1069 | (4) Plan+Year FE:  -0.889*  (-2.09) N=1069

## B. Full-sample split (Table XI-split design) on the common sample
                                  (1) Year FE, base           (2) Year FE, all            (3) Plan FE                 (4) Plan+Year FE            
Peer-adj    First half             -0.443   (-1.64)            -0.485   (-1.62)            -0.518   (-1.13)            -0.463   (-1.03)           
            Second half            -0.804** (-2.84)            -0.687** (-2.33)            -0.425   (-1.01)            -0.545   (-1.33)           
            p: first = second     0.361                       0.559                       0.758                       0.811                       
            N / adj R2            1240 / 0.069              1072 / 0.083              1069 / 0.088              1069 / 0.134              
Bench-adj   First half              0.004   ( 0.02)            -0.232   (-0.78)            -0.574   (-0.99)            -0.432   (-0.72)           
            Second half            -1.106** (-2.37)            -0.956***(-3.56)            -1.265** (-2.71)            -1.275***(-3.01)           
            p: first = second     0.095                       0.129                       0.215                       0.117                       
            N / adj R2            1240 / 0.138              1072 / 0.125              1069 / 0.013              1069 / 0.110              

## C. Conflicted-only (Table XI design) on the common sample
conflicted-only common sample: 227 CIO-years, 34 CIOs
  Peer-adj   (1) Year FE, base:  -0.422   (-1.47) N=202 | (2) Year FE, all:  -0.260   (-0.78) N=183 | (3) Plan FE:  -0.157   (-0.43) N=179 | (4) Plan+Year FE:  -0.482   (-0.96) N=179 | (5) CIO FE:  -0.781*  (-2.05) N=190 | (6) CIO FE, ten>=4:  -0.525   (-0.48) N=123
  Bench-adj  (1) Year FE, base:  -1.166** (-2.11) N=202 | (2) Year FE, all:  -1.030*  (-2.04) N=183 | (3) Plan FE:  -1.978*  (-2.10) N=179 | (4) Plan+Year FE:  -1.966** (-2.26) N=179 | (5) CIO FE:  -2.087*  (-1.82) N=190 | (6) CIO FE, ten>=4:  -4.211   (-1.38) N=123

## D. Same regressions, no controls (to separate sample from control effects), common sample
  Peer-adj   split yearFE: 1st  -0.302   (-1.04) 2nd  -0.882*  (-2.01) | split plan+yr: 1st  -0.267   (-0.62) 2nd  -0.684   (-1.59) | within-CIO:  -0.373   (-0.68)
  Bench-adj  split yearFE: 1st   0.253   ( 1.00) 2nd  -1.143** (-2.17) | split plan+yr: 1st  -0.118   (-0.22) 2nd  -1.407** (-2.63) | within-CIO:  -1.994** (-2.20)

## E. Correlation of the two measures in the common sample
  corr(peer-adj, bench-adj) all: 0.426 | conflicted only: 0.570 | within plan-year demeaned by year: 0.418
  conflicted CIOs, mean by half (common sample): peer-adj first -0.095 second -0.557 | bench-adj first 0.646 second -0.669
  plan's own benchmark return minus peer average, conflicted CIOs: first half 0.741, second half -0.112  (bench-adj = peer-adj + (peer avg - own benchmark))