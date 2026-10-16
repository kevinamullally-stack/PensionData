exec(open('xsec_setup_v2.py').read())     # S, young/highrate/highfund (missing coded missing), C1-C3, SPLITS (paper control lists), RAW
U=pd.read_pickle('underpaid_check.pkl')['S'][['ppd_id','fy','up_rc']]
S=S.merge(U,on=['ppd_id','fy'],how='left',validate='1:1')
NARROW=['size','l_fund']+C2                                   # size, lagged funding ratio, lagged allocations
PAPER={k:ctrls for k,sv,ctrls,cl,labs,tab in SPLITS}
SPL=[(k,sv,cl,labs,tab) for k,sv,ctrls,cl,labs,tab in SPLITS]
i=[s[0] for s in SPL].index('underpaid')
SPL.insert(i+1,('up_ann','up_rc',('ppd_id','fy'),('Underpaid (annual median)','Not Underpaid (annual median)'),'Table V, Panel C'))
PAPER['up_ann']=PAPER['underpaid']
def narrow(k): return [c for c in NARROW if not (k=='fund' and c=='l_fund')]   # the paper's funding block omits lagged funding
def est2(y, sv, ctrls, cl, fe, need=()):
    d, rhs = build(sv, ctrls)
    if need: d = d.dropna(subset=list(need))          # restrict to the sample with these variables non-missing
    d['_int']=d[cl[0]].astype(str)+'#'+d[cl[1]].astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in [cl[0],cl[1],'_int']}
    m=fits[cl[0]]; V=np.asarray(fits[cl[0]]._vcov)+np.asarray(fits[cl[1]]._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits[cl[0]]._G[0]),int(fits[cl[1]]._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat)
    def lc(wd):
        c=np.zeros(len(names))
        for k_,v in wd.items(): c[names.index(k_)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),G-1) if se>0 else np.nan
        return dict(est=e,se=se,t=t,p=p)
    return dict(a=lc({'g1_conf':1}), b=lc({'g0_conf':1}), d=lc({'g1_conf':1,'g0_conf':-1}), N=int(N), G=G, adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2))
VERS=[('narrow_fye','Narrow controls, fiscal-year-end FE',narrow,'fye_id'),
      ('narrow_fy','Narrow controls, year FE',narrow,'fy'),
      ('narrow_fye_ps','Narrow controls, fiscal-year-end FE, paper-controls sample',narrow,'fye_id'),
      ('paper_fye','Paper controls, fiscal-year-end FE',lambda k: PAPER[k],'fye_id'),
      ('paper_fy','Paper controls, year FE (published specification)',lambda k: PAPER[k],'fy')]
YS=[('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark')]
RES={v:{k:{y:est2(y,sv,cf(k),cl,fe,need=(PAPER[k] if v=='narrow_fye_ps' else ())) for y,_ in YS} for k,sv,cl,labs,tab in SPL} for v,_,cf,fe in VERS}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
for v,vl,_,_ in VERS:
    print(f"\n## {vl}")
    for k,sv,cl,(l1,l0),tab in SPL:
        print(f"{l1[:28]:28s}", ' || '.join(f"{y[:4]}: {fm(RES[v][k][y]['a'])} vs {fm(RES[v][k][y]['b'])} p={RES[v][k][y]['d']['p']:.3f} N={RES[v][k][y]['N']}" for y,_ in YS))
pd.to_pickle(dict(RES=RES,SPL=SPL,VERS=[(a,b,d) for a,b,_,d in VERS],YS=YS,NARROW=NARROW),'xsec_narrow_res.pkl')
