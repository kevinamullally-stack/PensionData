src=open('xsec_narrow.py').read().split("VERS=[")[0]     # setup, NARROW, PAPER, est2 (no estimation)
exec(src)
import statsmodels.formula.api as smf
FP=pd.read_pickle('df_newbench_v2.pkl')[['ppd_id','fy','CIO_TotalComp','size']].copy()
P=FP[FP.CIO_TotalComp.notna()].copy(); P['lc']=np.log(P.CIO_TotalComp)
# CPI-U, U.S. city average, annual average (BLS series CUUR0000SA0), 2001-2020
CPI={2001:177.1,2002:179.9,2003:184.0,2004:188.9,2005:195.3,2006:201.6,2007:207.342,2008:215.303,2009:214.537,2010:218.056,2011:224.939,2012:229.594,2013:232.957,2014:236.736,2015:237.017,2016:240.007,2017:245.120,2018:251.107,2019:255.657,2020:258.811}
P['real']=P.CIO_TotalComp*CPI[2020]/P.fy.map(CPI)
P=P[P.fy.isin(CPI)].copy()
P['res']=smf.ols('lc ~ size + C(fy)',data=P.dropna(subset=['size'])).fit().resid
def spct(x,p):   # Stata egen pctile / summarize, detail definition
    x=np.sort(np.asarray(x.dropna())); n=len(x); Pn=n*p/100
    return (x[int(Pn)-1]+x[int(Pn)])/2 if abs(Pn-round(Pn))<1e-9 else x[int(np.floor(Pn))]
q=lambda v,p: P.groupby('fy')[v].transform(lambda s: spct(s,100*p))
DEF={}   # 1 = lower-paid group, 0 = highly paid group
DEF['c_fixed']=(P.CIO_TotalComp<P.loc[P.fy.between(2009,2014),'CIO_TotalComp'].median()).astype(float)
DEF['c_annual']=(P.CIO_TotalComp<P.groupby('fy').CIO_TotalComp.transform('median')).astype(float)
DEF['c_real']=(P.real<P.real.median()).astype(float)
DEF['c_size']=np.where(P.res.isna(),np.nan,(P.res<P.groupby('fy').res.transform('median')).astype(float))
DEF['c_top3']=(P.CIO_TotalComp<q('CIO_TotalComp',0.6667)).astype(float)     # 0 = top third that year
DEF['c_top4']=(P.CIO_TotalComp<q('CIO_TotalComp',0.75)).astype(float)    # 0 = top quarter that year
DEF['c_bot3']=(P.CIO_TotalComp<q('CIO_TotalComp',0.3333)).astype(float)     # 1 = bottom third that year
for k,v in DEF.items(): P[k]=v
S=S.merge(P[['ppd_id','fy']+list(DEF)],on=['ppd_id','fy'],how='left',validate='1:1')
S['pay_spell']=S.cio.astype(str)+'|'+S.ppd_id.astype(str)
S=S.sort_values(['pay_spell','fy'])
for k in DEF: S[k]=S.groupby('pay_spell')[k].transform(lambda v: v.ffill().bfill())   # filled within spell, as Underpaid is
S=S.sort_values(['ppd_id','fy'])
CS=[('c_fixed','Below $224,578 (paper code: pooled 2009-14 median)','Lower-paid','Highly paid'),
    ('c_annual','Below the median of that fiscal year (paper text)','Lower-paid','Highly paid'),
    ('c_real','Below the pooled median of inflation-adjusted pay','Lower-paid','Highly paid'),
    ('c_size','Below the median pay given plan size (paper text)','Lower-paid','Highly paid'),
    ('c_top3','Top third of pay that year vs. rest','Rest','Top third'),
    ('c_top4','Top quarter of pay that year vs. rest','Rest','Top quarter'),
    ('c_bot3','Bottom third of pay that year vs. rest','Bottom third','Rest')]
YS=[('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark')]
CVERS=[('narrow_fye','Narrow controls, fiscal-year-end FE',lambda: narrow('x'),'fye_id'),
       ('paper_fy','Paper controls, year FE (published specification)',lambda: PAPER['underpaid'],'fy')]
CRES={v:{k:{y:est2(y,k,cf(),('ppd_id','fy'),fe) for y,_ in YS} for k,*_ in CS} for v,_,cf,fe in CVERS}
SH={k:(float(S[k].mean()), float(S.loc[S.conf_pen_vendor==1,k].mean()), int(S[k].notna().sum())) for k,*_ in CS}
SHP={k:S.groupby(pd.cut(S.fy,[2000,2008,2014,2020]))[k].mean().round(2).tolist() for k,*_ in CS}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
for v,vl,_,_ in CVERS:
    print(f"\n## {vl}   [lower-paid group x Conflicted vs highly paid group x Conflicted]")
    for k,lab,l1,l0 in CS:
        print(f"{lab[:52]:52s}", ' || '.join(f"{y[:4]}: {fm(CRES[v][k][y]['a'])} vs {fm(CRES[v][k][y]['b'])} p={CRES[v][k][y]['d']['p']:.3f} N={CRES[v][k][y]['N']}" for y,_ in YS))
print('\nshare in group 1 (all, conflicted, n) and by period 2001-08/2009-14/2015-20:')
for k,lab,l1,l0 in CS: print(f"  {lab[:52]:52s} {SH[k][0]:.2f} {SH[k][1]:.2f} n={SH[k][2]} | {SHP[k]}")
pd.to_pickle(dict(CRES=CRES,CS=CS,CVERS=[(a,b,d) for a,b,_,d in CVERS],SH=SH,SHP=SHP,CPI=CPI),'comp_splits_res.pkl')
