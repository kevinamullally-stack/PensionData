src=open("returns_halves_equal_weight.py").read().split("\nR={}\n")[0]; exec(src)          # S, D (departed CIOs with halves), tests(), RAW
# Equal-weighted halves tests with CIO (CIO-plan spell) and fiscal-year-end FE, all years and excluding FY2009-2014.
# Weights: each CIO-plan spell's two halves get equal total weight (1 per half), so with spell FE the Second Half coefficient
# is the equal-weighted mean of spell-level second-minus-first changes; fiscal-year-end FE net out common FYE shocks.
YS=[('peer_adj_ret100','Peer-Adjusted Return'),('b_AB','Benchmark-Adjusted Return')]
CTL=C1+C2+C5                                                      # lagged plan controls (CIO tenure/age and time-invariant traits excluded)
def fitw(y, rhs, fe, data, combos):
    d=data.dropna(subset=[y]+rhs).copy()
    for _ in range(10):
        n0=len(d)
        for gg in fe.replace(' ','').split('+'): d=d[d[gg].map(d[gg].value_counts())>1]
        if len(d)==n0: break
    d['w']=1.0/d.groupby(['cp','second']).cp.transform('size')     # equal weight per spell-half
    d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={c: pf.feols(f, data=d, weights='w', vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V=(np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov))*(N-1)/(N-K)*G/(G-1)
    w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    Vp=np.asarray(fits['ppd_id']._vcov)*(N-1)/(N-K)*int(fits['ppd_id']._G[0])/(int(fits['ppd_id']._G[0])-1)   # plan-only clustering as a check
    b=np.asarray(m._beta_hat); both=d.groupby('cp').second.nunique()==2
    out=dict(N=int(N),G=G,Gy=int(fits['fy']._G[0]),nsp_c=int(both[d.groupby('cp').conf.max()==1].sum()),nsp_o=int(both[d.groupby('cp').conf.max()==0].sum()))
    for nm,wd in combos.items():
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); sep=float(np.sqrt(max(c@Vp@c,0)))
        out[nm]=dict(est=e,t=e/se,p=2*stats.t.sf(abs(e/se),G-1),pp=2*stats.t.sf(abs(e/sep),int(fits['ppd_id']._G[0])-1))
    return out
D['conf']=D.groupby('cp').conf.transform('max')      # conflicted CIO-plan spell (as in the equal-weighted tests; includes the departure year)
D['conf_second']=D.conf*D.second
PER={'all':('All fiscal years',D.fy.notna()),'ex0914':('Excluding fiscal years 2009-2014',~D.fy.between(2009,2014))}
R={}
for per,(lab,mask) in PER.items():
    Dp=D[mask].copy(); Sp=S[S.fy.notna() if per=='all' else ~S.fy.between(2009,2014)]
    for y,_ in YS:
        Dp[y+'_dm']=Dp[y]-Sp.groupby('fye_id')[y].mean().reindex(Dp.fye_id).values          # net of the period's FYE mean (Table III sample)
        # (a) simple equal-weighted mean differences (as in returns_halves_equal_weight)
        def ud(v):
            d=Dp.dropna(subset=[v]); h=d.groupby(['cp','second'])[v].mean().unstack()
            return pd.DataFrame({'d':h[1.0]-h[0.0],'n':d.groupby('cp').size(),'conf':d.groupby('cp').conf.max(),'ppd_id':d.groupby('cp').ppd_id.first()}).dropna(subset=['d'])
        R[(per,y,'mean')]=tests(ud(y)); R[(per,y,'mean_dm')]=tests(ud(y+'_dm'))
        cmb={'oth':{'second':1},'cnf':{'second':1,'conf_second':1},'diff':{'conf_second':1}}
        R[(per,y,'fe_spell')]=fitw(y,['second','conf_second'],'cp',Dp,cmb)                    # = (a) up to singleton drops
        R[(per,y,'fe')]=fitw(y,['second','conf_second'],'cp + fye_id',Dp,cmb)
        R[(per,y,'fe_ctl')]=fitw(y,['second','conf_second']+CTL,'cp + fye_id',Dp,cmb)
        R[(per,y,'fe_conf')]=fitw(y,['second'],'cp + fye_id',Dp[Dp.conf==1],{'cnf':{'second':1}})
        R[(per,y,'fe_conf_ctl')]=fitw(y,['second']+CTL,'cp + fye_id',Dp[Dp.conf==1],{'cnf':{'second':1}})
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f(q): return f"{q['est']:+.3f}{st(q['p'])} (p {q['p']:.3f}; plan p {q['pp']:.3f})"
for per,(lab,_) in PER.items():
    print(f"\n==================== {lab}")
    for y,yl in YS:
        print(f"## {yl}")
        for k in ['mean','mean_dm']:
            r=R[(per,y,k)]; print(f"  {k:12s} conf {r['mc']:+.3f} (p0 {r['p1c']:.3f}) other {r['mo']:+.3f} (p0 {r['p1o']:.3f}) diff {r['diff']:+.3f}{st(r['p'])} p {r['p']:.3f} W {r['pw']:.3f} rank {r['prs']:.3f} | n {r['nc']}/{r['no']}")
        for k in ['fe_spell','fe','fe_ctl']:
            r=R[(per,y,k)]; print(f"  {k:12s} conf {f(r['cnf'])} | other {f(r['oth'])} | diff {f(r['diff'])} | N {r['N']} spells {r['nsp_c']}/{r['nsp_o']} Gy {r['Gy']}")
        for k in ['fe_conf','fe_conf_ctl']:
            r=R[(per,y,k)]; print(f"  {k:12s} conf {f(r['cnf'])} | N {r['N']} spells {r['nsp_c']} Gy {r['Gy']}")
pd.to_pickle(dict(R=R,YS=YS,PER={k:v[0] for k,v in PER.items()}),'returns_halves_equal_weight_fe.pkl')
