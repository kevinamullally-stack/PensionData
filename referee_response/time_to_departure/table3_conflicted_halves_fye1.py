exec(open('table3_conflicted_halves.py').read().split("VERS={")[0])           # data, halves, indicators, controls, cols()
S['spell']=S.cp
YS=[('peer_adj_ret100','Peer-Adjusted Return'),('b_AB','Benchmark-Adjusted Return')]
print('spells with varying Conflicted CIO:', int((S.groupby('cp').conf_pen_vendor.nunique()>1).sum()))
def pcols(c4):
    full=C1+C2+C3+c4+C5
    return [dict(x='conf_pen_vendor',ctrl=full,fe='fye_id',plan='No',cio='No',year='Yes'),
            dict(x='conf_pen_vendor',ctrl=full,fe='ppd_id',plan='Yes',cio='No',year='No'),
            dict(x='conf_pen_vendor',ctrl=full,fe='ppd_id + fye_id',plan='Yes',cio='No',year='Yes'),
            dict(x='conf_pen_vendor',ctrl=[v for v in full if v not in ('fincenter1','prior_private_exp','Elite_inst')],fe='spell + fye_id',plan='No',cio='Yes',year='Yes',within=True,same=c4)]   # time-invariant CIO and plan traits are absorbed by CIO FE
VERS={'paper':pcols(C4),'paper_noten':pcols(C4n)}
RAW=pf.ssc(adj=False,fixef_k='none',cluster_adj=False)
def nsp(dat,y,xv,fe):   # CIO-plan spells and CIOs left after dropping singleton fixed-effect groups
    d=dat.dropna(subset=[y]+xv)
    for _ in range(10):
        n0=len(d)
        for g_ in fe.replace(' ','').split('+'): d=d[d[g_].map(d[g_].value_counts())>1]
        if len(d)==n0: break
    return (d.cp.nunique(),d.cio.nunique())
def run(y,col):
    x=col['x']; within=col.get('within',False)
    # column 4: conflicted plan-years only (same rows as columns 1-3 otherwise), CIO + FYE FE; First Half is the reference
    dat=S[(S[x]==1)&S.second.notna()].dropna(subset=['fincenter1']+[v for v in col['same'] if v in ('prior_private_exp','Elite_inst')]) if within else S
    xs=[x+'_h2'] if within else [x+'_h1',x+'_h2']+([x+'_hu'] if S[x+'_hu'].sum()>0 else [])
    rhs=' + '.join(xs+col['ctrl'])
    fits={cl:pf.feols(f'{y} ~ {rhs} | {col["fe"]}',data=dat,vcov={'CRV1':cl},ssc=RAW) for cl in ['ppd_id','fy','py']}
    m=fits['ppd_id']; V=np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['py']._vcov)
    N=m._N; names=list(m._coefnames); G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); ren={x+'_h1':'h1',x+'_h2':'h2',x+'_hu':'hu'}
    est={ren.get(n,n):(float(b[i]),float(np.sqrt(max(V[i,i],0)))) for i,n in enumerate(names)}
    c=np.zeros(len(names)); c[names.index(x+'_h2')]=1
    if not within: c[names.index(x+'_h1')]=-1
    dd=float(c@b); se=float(np.sqrt(max(c@V@c,0)))
    mi=pf.feols(f'{y} ~ {rhs} | {col["fe"]}',data=dat,vcov='iid')
    return dict(est=est,diff=(dd,se),N=int(N),G=G,Gp=int(fits['ppd_id']._G[0]),Gy=int(fits['fy']._G[0]),ncio=nsp(dat,y,xs+col['ctrl'],col['fe']),adjr2=float(mi._adj_r2),col=col,within=within)
RES={(v,y):[run(y,c) for c in VERS[v]] for v in VERS for y,_ in YS}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def pv(b,se,G): t=b/se; return t,2*stats.t.sf(abs(t),G-1)
for v in VERS:
    for y,yl in YS:
        print(f"\n[{v}] {yl}")
        for k,l in [('h1','Conf x First'),('h2','Conf x Second')]:
            print(f"  {l:14s} "+' '.join((f"{r['est'][k][0]:7.3f}{st(pv(*r['est'][k],r['G'])[1]):3s}({pv(*r['est'][k],r['G'])[0]:5.2f})" if k in r['est'] else f"{'reference':>17s}") for r in RES[(v,y)]))
        print(f"  {'Second-First':14s} "+' '.join(f"{r['diff'][0]:7.3f}{st(pv(*r['diff'],r['G'])[1]):3s}(p{pv(*r['diff'],r['G'])[1]:.3f})" for r in RES[(v,y)]))
        print(f"  {'N':14s} "+' '.join(f"{r['N']:>17d}" for r in RES[(v,y)]))
        print(f"  {'clusters p/y, spells':14s} "+' '.join(f"{r['Gp']:>6d}/{r['Gy']}/{r['ncio'][0]}/{r['ncio'][1]}" for r in RES[(v,y)]))
        print(f"  {'controls kept':14s} "+' '.join(f"{len(r['est']):>17d}" for r in RES[(v,y)]))
pd.to_pickle(dict(RES=RES,YS=YS,NC={x:dict(h1=int(S[x+'_h1'].sum()),h2=int(S[x+'_h2'].sum()),hu=int(S[x+'_hu'].sum())) for x in ['conf_pen_vendor']}),'table3_conflicted_halves_fye1.pkl')
