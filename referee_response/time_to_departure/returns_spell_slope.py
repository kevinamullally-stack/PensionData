src=open("returns_halves_equal_weight.py").read().split("\nR={}\n")[0]; exec(src)          # S, D, unit_diffs(), tests(), fit()
# Spell-level performance slope: each CIO-plan spell's OLS slope of return on fiscal year (pp per year), departed CIOs, Table III sample
S['eq_pct']=100*S.EQTotal_Actl; S['fi_pct']=100*S.FITotal_Actl
P=S[S.curr==0].copy(); P['conf']=P.conf_pen_vendor.astype(float)
YS=[('peer_adj_ret100','Peer-Adjusted Return'),('b_AB','Benchmark-Adjusted Return')]
for y,_ in YS: P[y+'_dm']=P[y]-S.groupby('fye_id')[y].transform('mean').reindex(P.index)
def slopes(y, minobs=3, unit='spell', wins=True, extra=()):
    d=P.dropna(subset=[y]+list(extra))
    if unit=='cio':
        d=d.groupby(['cio','fy'],as_index=False).agg(**{y:(y,'mean')},conf=('conf','max'),ppd_id=('ppd_id','first')); key='cio'
    else: key='cp'
    rows=[]
    for k,g in d.sort_values('fy').groupby(key):
        if g.fy.nunique()<minobs: continue
        f=g.fy.astype(float)
        r_=dict(key=k,slope=np.polyfit(f,g[y].astype(float),1)[0],n=len(g),conf=float(g.conf.max()),ppd_id=g.ppd_id.iloc[0],y0=float(g[y].iloc[0]),ybar=float(g[y].mean()))
        for v in extra: r_['s_'+v]=np.polyfit(f,g[v].astype(float),1)[0]
        rows.append(r_)
    T=pd.DataFrame(rows); lo,hi=T.slope.quantile([.01,.99]); T['d']=T.slope.clip(lo,hi) if wins else T.slope
    for v in extra: lo,hi=T['s_'+v].quantile([.01,.99]); T['s_'+v]=T['s_'+v].clip(lo,hi)
    return T
def ols(T, x):
    m=sm.OLS(T.d.astype(float),sm.add_constant(T[['conf']+x].astype(float))).fit(cov_type='cluster',cov_kwds={'groups':T.ppd_id})
    return dict(diff=m.params['conf'],p=m.pvalues['conf'],n=int(m.nobs),coefs={k:(m.params[k],m.pvalues[k]) for k in x})
A={}; X={}; BYLEN={}; C={}; RATE={}
for y,_ in YS:
    for k in [2,3,4,6,8]: A[(y,f'min{k}')]=tests(slopes(y,k))
    T3=slopes(y,3)
    A[(y,'dm')]=tests(slopes(y+'_dm',3)); A[(y,'cio')]=tests(slopes(y,3,'cio')); A[(y,'nowins')]=tests(slopes(y,3,wins=False))
    for k in [3,5]: A[(y,f'dropneg{k}')]=tests(T3,k,'neg'); A[(y,f'droppos{k}')]=tests(T3,k,'pos')
    # mean reversion: control for the spell's first-year return; allocation drift: control for the spell's own equity/fixed income/alternatives slopes
    X[(y,'none')]=ols(T3,[]); X[(y,'y0')]=ols(T3,['y0'])
    Ta=slopes(y,3,extra=('eq_pct','fi_pct','alt_pct')); X[(y,'none_a')]=ols(Ta,[]); X[(y,'alloc')]=ols(Ta,['s_eq_pct','s_fi_pct','s_alt_pct'])
    X[(y,'both')]=ols(Ta,['y0','s_eq_pct','s_fi_pct','s_alt_pct'])
    T3['len']=pd.cut(T3.n,[2,3,5,8,30],labels=['3','4-5','6-8','9+'])
    BYLEN[y]=T3.groupby(['len','conf'],observed=False).d.agg(['mean','count']).unstack()
    # plan-year-weighted designs
    P['t']=P.fy.astype(float)-2010; P['conf_t']=P.conf*P.t
    C[(y,'pool')]=fit(y,['t','conf_t'],'cp',P,{'b':{'conf_t':1},'oth':{'t':1},'cnf':{'t':1,'conf_t':1}})
    C[(y,'pool_fye')]=fit(y,['conf_t'],'cp + fye_id',P,{'b':{'conf_t':1}})
    H=P[P.second.notna()].copy(); H['conf_second']=H.conf*H.second
    C[(y,'halves')]=fit(y,['second','conf_second'],'cp',H,{'b':{'conf_second':1},'oth':{'second':1},'cnf':{'second':1,'conf_second':1}})
    C[(y,'halves_fye')]=fit(y,['second','conf_second'],'cp + fye_id',H,{'b':{'conf_second':1}})
    # halves change per year between half midpoints (equal weight per spell)
    d=D.dropna(subset=[y]); h=d.groupby(['cp','second'])[[y,'fy']].mean().unstack()
    T=pd.DataFrame({'chg':h[(y,1.0)]-h[(y,0.0)],'gap':h[('fy',1.0)]-h[('fy',0.0)]})
    T['n']=d.groupby('cp').size(); T['conf']=d.groupby('cp').conf.max(); T['ppd_id']=d.groupby('cp').ppd_id.first(); T=T.dropna(); T['d']=T.chg/T.gap
    RATE[y]=tests(T); RATE[y]['gapc']=T[T.conf==1].gap.mean(); RATE[y]['gapo']=T[T.conf==0].gap.mean()
# levels behind the slope: first-year, mean and last-year return of spells with at least 3 years
LEV={}
for y,_ in YS:
    d=P.dropna(subset=[y]).sort_values('fy'); g=d.groupby('cp')
    T=pd.DataFrame({'first':g[y].first(),'mean':g[y].mean(),'last':g[y].last(),'conf':g.conf.max(),'n':g.size()}); T=T[T.n>=3]
    LEV[y]={k:dict(c=T.loc[T.conf==1,k].mean(),o=T.loc[T.conf==0,k].mean(),p=ttest_ind(T.loc[T.conf==1,k],T.loc[T.conf==0,k]).pvalue,nc=int((T.conf==1).sum()),no=int((T.conf==0).sum())) for k in ['first','mean','last']}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
for y,yl in YS:
    print(f"\n######## {yl}: spell-level slope (pp per year)")
    for k in ['min2','min3','min4','min6','min8','dm','cio','nowins','dropneg3','droppos3','dropneg5','droppos5']:
        r=A[(y,k)]; print(f"  {k:9s} conf {r['mc']:+.3f} (p0 {r['p1c']:.3f}; med {r['medc']:+.3f}) other {r['mo']:+.3f} (p0 {r['p1o']:.3f}; med {r['medo']:+.3f}) | diff {r['diff']:+.3f}{st(r['p'])} p {r['p']:.3f} W {r['pw']:.3f} rank {r['prs']:.3f} | wtd {r['wdiff']:+.3f} p {r['wp']:.3f} | rising {1-r['negc']:.2f}/{1-r['nego']:.2f} | n {r['nc']}/{r['no']}")
    for k in ['none','y0','none_a','alloc','both']:
        q=X[(y,k)]; print(f"  ctl {k:5s} diff {q['diff']:+.3f}{st(q['p'])} p {q['p']:.3f} n {q['n']} | "+' '.join(f"{a} {b:+.3f} ({p:.3f})" for a,(b,p) in q['coefs'].items()))
    print(BYLEN[y].round(3).to_string())
    for k in ['pool','pool_fye','halves','halves_fye']:
        q=C[(y,k)]['b']; print(f"  {k:10s} conflicted extra {q['est']:+.3f}{st(q['p'])} t {q['t']:.2f} p {q['p']:.3f} N {C[(y,k)]['N']}")
    r=RATE[y]; print(f"  per-year halves rate: conf {r['mc']:+.3f} other {r['mo']:+.3f} diff {r['diff']:+.3f} p {r['p']:.3f} W {r['pw']:.3f} rank {r['prs']:.3f} | gap {r['gapc']:.2f}/{r['gapo']:.2f}")
pd.to_pickle(dict(LEV=LEV,A=A,X=X,BYLEN=BYLEN,C=C,RATE=RATE,YS=YS,nP={y:int(P[y].notna().sum()) for y,_ in YS},nsp={y:P.dropna(subset=[y]).cp.nunique() for y,_ in YS}),'returns_spell_slope.pkl')
