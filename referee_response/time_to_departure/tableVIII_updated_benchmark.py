src=open('shock_tests.py').read().split("FES=[('fy'")[0]; exec(src)     # S, CTL (Table VIII controls), YS, fit()
FES=[('fy','No','Yes','No'),('ppd_id','Yes','No','No'),('ppd_id + fy','Yes','Yes','No'),('fye_id','No','No','Yes'),('ppd_id + fye_id','Yes','No','Yes')]
T8={}
for y,_ in YS:
    for fe,*_ in FES:
        T8[(y,fe)]=fit(y,['conf','confxshock','shock']+CTL,fe,{'conf':{'conf':1},'cxs':{'confxshock':1},'shock':{'shock':1},'sum':{'conf':1,'confxshock':1}})
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
for y,yl in YS:
    print(f"\n## {yl}")
    for lab,k in [('Conflicted CIO','conf'),('Conflicted x Shock Period','cxs'),('Shock Period','shock')]:
        print(f"{lab:28s}"+''.join(f"{T8[(y,fe)][k]['est']:>9.3f}{st(T8[(y,fe)][k]['p']):3s}({T8[(y,fe)][k]['t']:5.2f})" for fe,*_ in FES))
    print(f"{'Conflicted + Interaction':28s}"+''.join(f"{T8[(y,fe)]['sum']['est']:>9.3f}   p={T8[(y,fe)]['sum']['p']:.3f}  " for fe,*_ in FES))
    print(f"{'N / adj R2':28s}"+''.join(f"{T8[(y,fe)]['N']:>9d} {T8[(y,fe)]['adjr2']:.3f}      " for fe,*_ in FES))
pd.to_pickle(dict(T8=T8,YS=YS,FES=FES),'tableVIII_bench.pkl')

# plan-clustered check (same point estimates)
def plan_only(y, fe):
    d=S.dropna(subset=[y,'conf','confxshock','shock']+CTL).copy()
    for g in fe.replace(' ','').split('+'): d=d[d[g].map(d[g].value_counts())>1].copy()
    f=f"{y} ~ conf + confxshock + shock + {' + '.join(CTL)} | {fe}"
    m=pf.feols(f, data=d, vcov={'CRV1':'ppd_id'}, ssc=RAW); names=list(m._coefnames); N=m._N; K=len(names)+1; G=int(m._G[0])
    V=np.asarray(m._vcov)*(N-1)/(N-K)*G/(G-1); b=np.asarray(m._beta_hat); out={}
    for k,wd in {'conf':{'conf':1},'cxs':{'confxshock':1},'sum':{'conf':1,'confxshock':1}}.items():
        c=np.zeros(len(names))
        for n,v in wd.items(): c[names.index(n)]=v
        e=float(c@b); se=float(np.sqrt(c@V@c)); out[k]=dict(est=e,se=se,t=e/se,p=2*stats.t.sf(abs(e/se),G-1))
    out['G']=G; return out
PLAN={(y,fe):plan_only(y,fe) for y,_ in YS for fe,*_ in FES}
for y,yl in YS:
    print(f"plan-clustered t ({yl[:12]}):", ' | '.join(f"conf {PLAN[(y,fe)]['conf']['t']:.2f}, cxs {PLAN[(y,fe)]['cxs']['t']:.2f}, sum {PLAN[(y,fe)]['sum']['t']:.2f} (p {PLAN[(y,fe)]['sum']['p']:.3f})" for fe,*_ in FES))
pd.to_pickle(dict(T8=T8,YS=YS,FES=FES,PLAN=PLAN),'tableVIII_bench.pkl')
