exec(open('table3_conflicted_halves_fye1.py').read().split("RES={(v,y)")[0])     # data, halves, run(), VERS (paper, paper_noten)
# Table III halves split (FYE FE paper table) on sample periods that avoid the 2009-2014 shock years
S_full=S.copy()
PER={'pre2009':('Fiscal years through 2008',S_full.fy<=2008),'ex0914':('Excluding fiscal years 2009-2014',~S_full.fy.between(2009,2014))}
def plan_p(y,col,dat):   # one-way plan clustering, as a check on the few year clusters
    x=col['x']; within=col.get('within',False)
    xs=[x+'_h2'] if within else [x+'_h1',x+'_h2']+([x+'_hu'] if dat[x+'_hu'].sum()>0 else [])
    m=pf.feols(f'{y} ~ {" + ".join(xs+col["ctrl"])} | {col["fe"]}',data=dat,vcov={'CRV1':'ppd_id'})
    n=list(m._coefnames); b=np.asarray(m._beta_hat); V=np.asarray(m._vcov); G=int(m._G[0]); out={}
    for k,cv in [('h1',{x+'_h1':1}),('h2',{x+'_h2':1}),('diff',{x+'_h2':1} if within else {x+'_h2':1,x+'_h1':-1})]:
        if any(v not in n for v in cv): continue
        c=np.zeros(len(n))
        for v,w_ in cv.items(): c[n.index(v)]=w_
        e=c@b; se=np.sqrt(c@V@c); out[k]=2*stats.t.sf(abs(e/se),G-1)
    return out
RES={}; CNT={}
for per,(lab,mask) in PER.items():
    S=S_full[mask].copy()
    CNT[per]=dict(rows=len(S),h1=int(S.conf_pen_vendor_h1.sum()),h2=int(S.conf_pen_vendor_h2.sum()))
    for v in VERS:
        for y,_ in YS:
            regs=[]
            for col in VERS[v]:
                r=run(y,col)
                dat=S[(S[col['x']]==1)&S.second.notna()].dropna(subset=['fincenter1','prior_private_exp','Elite_inst']) if col.get('within') else S
                r['pp']=plan_p(y,col,dat); regs.append(r)
            RES[(per,v,y)]=regs
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def pv(b,se,G): t=b/se; return t,2*stats.t.sf(abs(t),G-1)
for per,(lab,_) in PER.items():
    print(f"\n==================== {lab}: rows {CNT[per]['rows']}, conflicted first {CNT[per]['h1']}, second {CNT[per]['h2']}")
    for v in VERS:
        for y,yl in YS:
            regs=RES[(per,v,y)]; print(f"[{v}] {yl}")
            for k,l in [('h1','Conf x First'),('h2','Conf x Second')]:
                print(f"  {l:14s} "+' '.join((f"{r['est'][k][0]:7.3f}{st(pv(*r['est'][k],r['G'])[1]):3s}({pv(*r['est'][k],r['G'])[0]:5.2f}) pp{r['pp'].get(k,np.nan):.2f}" if k in r['est'] else f"{'reference':>25s}") for r in regs))
            print(f"  {'Second-First':14s} "+' '.join(f"{r['diff'][0]:7.3f}{st(pv(*r['diff'],r['G'])[1]):3s}(p{pv(*r['diff'],r['G'])[1]:.3f}) pp{r['pp']['diff']:.2f}" for r in regs))
            print(f"  {'N; G p/y; spells/CIOs':14s} "+' '.join(f"{r['N']:>6d}; {r['Gp']}/{r['Gy']}; {r['ncio'][0]}/{r['ncio'][1]}" for r in regs))
pd.to_pickle(dict(RES=RES,YS=YS,CNT=CNT,PER={k:v[0] for k,v in PER.items()}),'table3_conflicted_halves_preshock.pkl')
