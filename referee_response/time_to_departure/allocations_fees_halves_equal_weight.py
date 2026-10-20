src=open("returns_halves_equal_weight.py").read().split("\nR={}\n")[0]; exec(src)          # S, D, unit_diffs(), tests()
# --- outcomes on the Table III sample ---
S['eq_pct']=100*S.EQTotal_Actl; S['fi_pct']=100*S.FITotal_Actl; S['re_pct']=100*S.RETotal_Actl
ALL7=['eq_pct','fi_pct','re_pct','pe_pct','hf_pct','am_pct','cm_pct']
S['am_pct']=100*S.AltMiscTotal_Actl; S['cm_pct']=100*S.COMDTotal_Actl
# fee net of allocations: residual from a pooled regression on the Table III sample (two steps, as in Table IX but with pooled allocation coefficients)
def resid(rhs, fe=None):
    d=S.dropna(subset=['fee_ratio_pct']+rhs)
    X=d[rhs].astype(float)
    if fe: X=pd.concat([X,pd.get_dummies(d[fe],prefix='fe',drop_first=True).astype(float)],axis=1)
    m=sm.OLS(d.fee_ratio_pct.astype(float),sm.add_constant(X)).fit()
    out=pd.Series(np.nan,index=S.index); out.loc[d.index]=m.resid.values
    return out, m
S['fee_r3'],m3=resid(['eq_pct','fi_pct','alt_pct'])
S['fee_r3fe'],m3fe=resid(['eq_pct','fi_pct','alt_pct'],'fye_id')
S['fee_r7fe'],m7fe=resid(ALL7,'fye_id')
print('allocation coefficients (fee on EQ, FI, Alt, pooled):', {k:round(v,4) for k,v in m3.params.items() if not str(k).startswith('fe_')})
OUT2=[('eq_pct','Equity Allocation (%)'),('fi_pct','Fixed Income Allocation (%)'),('alt_pct','Alternatives Allocation (%)'),('re_pct','Real Estate Allocation (%)'),('pe_pct','Private Equity Allocation (%)'),('hf_pct','Hedge Fund Allocation (%)'),
      ('fee_ratio_pct','Fee Ratio (%)'),('fee_r3','Fee Ratio net of equity, fixed income and alternatives shares'),('fee_r3fe','Fee Ratio net of the three shares and FYE effects'),('fee_r7fe','Fee Ratio net of all seven asset-class shares and FYE effects')]
D=S[(S.curr==0)&S.second.notna()].copy(); D['conf']=D.conf_pen_vendor.astype(float)
for y,_ in OUT2: D[y+'_dm']=D[y]-S.groupby('fye_id')[y].transform('mean').reindex(D.index)
R={}
for y,_ in OUT2:
    for unit in ['spell','cio']:
        R[(y,unit,'base')]=tests(unit_diffs(y,unit)); R[(y,unit,'ten4')]=tests(unit_diffs(y,unit,4)); R[(y,unit,'dm')]=tests(unit_diffs(y+'_dm',unit))
        T=unit_diffs(y,unit)
        for k in [3,5]: R[(y,unit,f'dropneg{k}')]=tests(T,k,'neg'); R[(y,unit,f'droppos{k}')]=tests(T,k,'pos')
SL={}
for y,_ in OUT2:
    rows=[]
    for cp_,g in S[S.curr==0].dropna(subset=[y]).groupby('cp'):
        if g.fy.nunique()<3: continue
        rows.append(dict(slope=np.polyfit(g.fy.astype(float),g[y].astype(float),1)[0],n=len(g),conf=float(g.conf_pen_vendor.iloc[0]),ppd_id=g.ppd_id.iloc[0]))
    T=pd.DataFrame(rows); lo,hi=T.slope.quantile([.01,.99]); T['d']=T.slope.clip(lo,hi); SL[y]=tests(T)
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
for y,yl in OUT2:
    print(f"\n## {yl}")
    for unit in ['spell','cio']:
        for k in ['base','ten4','dm','dropneg3','droppos3']:
            r=R[(y,unit,k)]
            print(f"  [{unit:5s}] {k:9s} conf {r['mc']:+.3f} (p0 {r['p1c']:.3f}; med {r['medc']:+.3f} SR {r['psr']:.3f}; n {r['nc']}) | other {r['mo']:+.3f} (p0 {r['p1o']:.3f}) | diff {r['diff']:+.3f}{st(r['p'])} p {r['p']:.3f} Welch {r['pw']:.3f} rank {r['prs']:.3f} | wtd {r['wdiff']:+.3f} p {r['wp']:.3f}")
    r=SL[y]; print(f"  [slope] conf {r['mc']:+.4f} other {r['mo']:+.4f} diff {r['diff']:+.4f}{st(r['p'])} p {r['p']:.3f} Welch {r['pw']:.3f} | medians {r['medc']:+.4f}/{r['medo']:+.4f} rank {r['prs']:.3f} | wtd {r['wdiff']:+.4f} p {r['wp']:.3f} | n {r['nc']}/{r['no']}")
# --- fee change per year between half midpoints, and fee change regressed on each spell's own allocation changes ---
FEES=['fee_ratio_pct','fee_r3','fee_r3fe','fee_r7fe']
def spell_halves(cols):
    d=D.dropna(subset=cols)
    h=d.groupby(['cp','second'])[cols+['fy']].mean().unstack()
    T=pd.DataFrame({c:h[(c,1.0)]-h[(c,0.0)] for c in cols+['fy']}).rename(columns={'fy':'gap'})
    T['n']=d.groupby('cp').size(); T['conf']=d.groupby('cp').conf.max(); T['ppd_id']=d.groupby('cp').ppd_id.first()
    return T.dropna()
def ols_conf(T, y, x):
    m=sm.OLS(T[y].astype(float),sm.add_constant(T[['conf']+x].astype(float))).fit(cov_type='cluster',cov_kwds={'groups':T.ppd_id})
    return dict(b=m.params['conf'],p=m.pvalues['conf'],n=int(m.nobs),coefs={k:(m.params[k],m.pvalues[k]) for k in x})
RATE={}; REG={}
for y in FEES:
    T=spell_halves([y]); T['d']=T[y]/T.gap
    RATE[y]=tests(T); RATE[y]['gapc']=T[T.conf==1].gap.mean(); RATE[y]['gapo']=T[T.conf==0].gap.mean()
    T=spell_halves([y,'eq_pct','fi_pct','alt_pct'])
    REG[(y,'halves')]=ols_conf(T,y,['eq_pct','fi_pct','alt_pct'])
    rows=[]
    for cp_,g in S[S.curr==0].dropna(subset=[y,'eq_pct','fi_pct','alt_pct']).groupby('cp'):
        if g.fy.nunique()<3: continue
        r_=dict(n=len(g),conf=float(g.conf_pen_vendor.iloc[0]),ppd_id=g.ppd_id.iloc[0])
        for v in [y,'eq_pct','fi_pct','alt_pct']: r_[v]=np.polyfit(g.fy.astype(float),g[v].astype(float),1)[0]
        rows.append(r_)
    T=pd.DataFrame(rows)
    for v in [y,'eq_pct','fi_pct','alt_pct']: lo,hi=T[v].quantile([.01,.99]); T[v]=T[v].clip(lo,hi)
    REG[(y,'slope')]=ols_conf(T,y,['eq_pct','fi_pct','alt_pct'])
for y in FEES:
    r=RATE[y]; print(f"{y:14s} per-year rate: conf {r['mc']:+.4f} other {r['mo']:+.4f} diff {r['diff']:+.4f} p {r['p']:.3f} Welch {r['pw']:.3f} rank {r['prs']:.3f} | gap {r['gapc']:.2f}/{r['gapo']:.2f}")
    for k in ['halves','slope']:
        q=REG[(y,k)]; print(f"   {k:6s} change on Conflicted + own allocation changes: {q['b']:+.4f} p {q['p']:.3f} n {q['n']} | "+' '.join(f"{a} {b:+.4f} ({p:.3f})" for a,(b,p) in q['coefs'].items()))
pd.to_pickle(dict(R=R,SL=SL,YS=OUT2,RATE=RATE,REG=REG,coef3={k:float(v) for k,v in m3.params.items()}),'alloc_fee_halves_ew.pkl')
