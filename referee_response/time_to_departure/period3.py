src=open('comp_splits.py').read().split("CS=[")[0]; exec(src)      # S with c_* pay definitions filled within spell; NARROW, C1-C3
C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']; FULL=C1+C2+C3+C4+C5
S['log_comp']=np.log(S.CIO_TotalComp)
S['p1']=(S.fy<=2008).astype(float); S['p2']=S.fy.between(2009,2014).astype(float); S['p3']=(S.fy>=2015).astype(float)
S['conf']=S.conf_pen_vendor.astype(float)
for k in ['p1','p2','p3']: S[f'conf_{k}']=S.conf*S[k]
S['conf_rest']=S.conf*(1-S.p2)
def fitlc(y, rhs, fe, combos, data=None):
    d=(S if data is None else data).dropna(subset=[y]+rhs).copy()
    for g in fe.replace(' ','').split('+'): d=d[d[g].map(d[g].value_counts())>1].copy()
    d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; V=np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); out=dict(N=int(N),G=G,adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2))
    for nm,wd in combos.items():
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se; out[nm]=dict(est=e,se=se,t=t,p=2*stats.t.sf(abs(t),G-1))
    return out
YS=[('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark')]
SPECS=[('t3_fy','All Table III controls, year FE (Table III col. 2)',FULL,'fy'),
       ('t3_fye','All Table III controls, fiscal-year-end FE',FULL,'fye_id'),
       ('nar_fye','Narrow controls, fiscal-year-end FE',NARROW,'fye_id')]
P3={}
for s,sl,ctl,fe in SPECS:
    for y,_ in YS:
        a=fitlc(y,['conf_p1','conf_p2','conf_p3']+ctl,fe,{'b1':{'conf_p1':1},'b2':{'conf_p2':1},'b3':{'conf_p3':1},'d21':{'conf_p2':1,'conf_p1':-1},'d23':{'conf_p2':1,'conf_p3':-1},'d13':{'conf_p1':1,'conf_p3':-1}})
        bb=fitlc(y,['conf_p2','conf_rest']+ctl,fe,{'mid':{'conf_p2':1},'rest':{'conf_rest':1},'d':{'conf_p2':1,'conf_rest':-1}})
        P3[(s,y)]=dict(three=a,two=bb)
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
print('conflicted plan-years by period:', [int(S.loc[S[k]==1,'conf'].sum()) for k in ['p1','p2','p3']], '| CIOs:', [S.loc[(S[k]==1)&(S.conf==1),'cio'].nunique() for k in ['p1','p2','p3']])
for s,sl,_,_ in SPECS:
    print(f"\n## {sl}")
    for y,yl in YS:
        a=P3[(s,y)]['three']; bb=P3[(s,y)]['two']
        print(f"{yl[:14]:14s} 2001-08 {fm(a['b1'])} | 2009-14 {fm(a['b2'])} | 2015-20 {fm(a['b3'])} | p(09-14=01-08) {a['d21']['p']:.3f} p(09-14=15-20) {a['d23']['p']:.3f} p(01-08=15-20) {a['d13']['p']:.3f} || other years {fm(bb['rest'])} p(09-14=other) {bb['d']['p']:.3f} | N {a['N']}")
# pay moderation with the conflict effect allowed to differ by period (interaction spec: all controls + fye1 FE)
XS=[('underpaid','Underpaid (paper variable)'),('c_real','Underpaid, inflation-adjusted median'),('c_annual','Underpaid, annual median'),('log_comp','Log CIO total comp. (reported years)')]
PM={}
for xv,xl in XS:
    d=S.dropna(subset=[xv]).copy(); d['X']=d[xv]-(d[xv].mean() if xv=='log_comp' else 0); d['confX']=d.conf*d.X
    for k in ['p2','p3']: d[f'cpc_{k}']=d.conf*(d[k]-d[k].mean())
    ctl=[c for c in FULL if c!=xv]
    for y,_ in YS:
        base=fitlc(y,['conf','confX','X']+ctl,'fye_id',{'confX':{'confX':1}},data=d)
        per=fitlc(y,['conf','confX','X','cpc_p2','cpc_p3']+ctl,'fye_id',{'confX':{'confX':1},'cp2':{'cpc_p2':1},'cp3':{'cpc_p3':1}},data=d)
        PM[(xv,y)]=dict(base=base,per=per)
print("\n## Pay interaction (all controls + fye1 FE): Conflicted x X, without and with Conflicted x period indicators")
for xv,xl in XS:
    print(f"{xl[:40]:40s}", ' || '.join(f"{y[:4]}: {fm(PM[(xv,y)]['base']['confX'])} -> {fm(PM[(xv,y)]['per']['confX'])} N {PM[(xv,y)]['per']['N']}" for y,_ in YS))
pd.to_pickle(dict(P3=P3,PM=PM,SPECS=[(a,b,d) for a,b,_,d in SPECS],XS=XS,YS=YS),'period3_res.pkl')
