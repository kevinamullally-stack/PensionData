exec(open('xsec_setup_v2.py').read())          # S = Table III sample with b_AB, controls C1-C3, RAW
CTL=C1+C2+C3+['l_log_cio_age','l_log_cio_tenure','l_sib1','wstate_political']   # globals in effect at the do-file's Table 5b
BASE,PRE,POST=2017,2005,2017
S['conf']=S.conf_pen_vendor.astype(float)
S['pre_bin']=S.conf*(S.fy<PRE); S['post_bin']=S.conf*(S.fy>POST)
YRS=[y for y in range(PRE,POST+1) if y!=BASE]
for y in YRS: S[f'conf_yr_{y}']=S.conf*(S.fy==y)
EV=['pre_bin']+[f'conf_yr_{y}' for y in YRS]+['post_bin']
SHOCK0,SHOCK1=2009,2013                                    # shock2 = 1 in FY2009-2013
PREV=['pre_bin']+[f'conf_yr_{y}' for y in YRS if y<SHOCK0]
SHOCKV=[f'conf_yr_{y}' for y in YRS if SHOCK0<=y<=SHOCK1]
LATEV=[f'conf_yr_{y}' for y in YRS if y>SHOCK1]+['post_bin']
def es(y, fe):
    d=S.dropna(subset=[y]+EV+CTL).copy()
    for _ in range(3):
        for g in fe.replace(' ','').split('+'): d=d[d[g].map(d[g].value_counts())>1].copy()
    d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(EV+CTL)} | {fe}'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V=(np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov))*(N-1)/(N-K)*G/(G-1)
    w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); out=dict(N=int(N),G=G,adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2),coef={})
    tc=stats.t.ppf(0.975,G-1)
    for v in EV:
        i=names.index(v); se=float(np.sqrt(max(V[i,i],0))); out['coef'][v]=dict(est=float(b[i]),se=se,t=float(b[i])/se,p=2*stats.t.sf(abs(b[i]/se),G-1),lo=float(b[i])-tc*se,hi=float(b[i])+tc*se)
    def wald(vs):
        ix=[names.index(v) for v in vs]; bb=b[ix]; VV=V[np.ix_(ix,ix)]
        Fst=float(bb@np.linalg.pinv(VV)@bb)/len(ix); return dict(F=Fst,p=float(stats.f.sf(Fst,len(ix),G-1)),q=len(ix))
    out['pre']=wald(PREV); out['shock']=wald(SHOCKV); out['late']=wald(LATEV)
    ref=names.index('conf_yr_2008'); Rm=[]
    for v in PREV:
        if v=='conf_yr_2008': continue
        r_=np.zeros(len(names)); r_[names.index(v)]=1; r_[ref]=-1; Rm.append(r_)
    Rm=np.array(Rm); rb=Rm@b; Fst=float(rb@np.linalg.pinv(Rm@V@Rm.T)@rb)/len(Rm); out['preflat']=dict(F=Fst,p=float(stats.f.sf(Fst,len(Rm),G-1)),q=len(Rm))
    # drop in the conflict effect: mean of FY2005-2008 minus mean of FY2009-2013 coefficients
    c=np.zeros(len(names)); pre_yrs=[v for v in PREV if v!='pre_bin']
    for v in pre_yrs: c[names.index(v)]+=1/len(pre_yrs)
    for v in SHOCKV: c[names.index(v)]-=1/len(SHOCKV)
    e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); out['contrast']=dict(est=e,se=se,t=e/se,p=2*stats.t.sf(abs(e/se),G-1))
    return out
YS=[('peer_adj_ret100','Peer-adjusted return'),('b_AB','Benchmark-adjusted return (updated benchmark)')]
SPECS=[('fy','Year FE'),('ppd_id','Plan FE'),('ppd_id + fy','Plan and year FE')]
ES={(y,fe):es(y,fe) for y,_ in YS for fe,_ in SPECS}
for y,yl in YS:
    print(f"\n## {yl}")
    print(f"{'':12s}"+''.join(f"{sl:>24s}" for _,sl in SPECS))
    for v in EV:
        print(f"{v:12s}"+''.join(f"{ES[(y,fe)]['coef'][v]['est']:>10.3f} ({ES[(y,fe)]['coef'][v]['t']:5.2f})       " for fe,_ in SPECS))
    for k,lab in [('pre','pre-shock=0 p'),('preflat','pre equal p'),('shock','shock=0 p'),('late','late=0 p')]:
        print(f"{lab:12s}"+''.join(f"{ES[(y,fe)][k]['p']:>24.3f}" for fe,_ in SPECS))
    print(f"{'pre - shock':12s}"+''.join(f"{ES[(y,fe)]['contrast']['est']:>10.3f} ({ES[(y,fe)]['contrast']['t']:5.2f})       " for fe,_ in SPECS))
    print(f"{'N':12s}"+''.join(f"{ES[(y,fe)]['N']:>24d}" for fe,_ in SPECS))
pd.to_pickle(dict(ES=ES,EV=EV,YRS=YRS,YS=YS,SPECS=SPECS,BASE=BASE,PRE=PRE,POST=POST,SHOCK=(SHOCK0,SHOCK1)),'es_shock_b2017.pkl')
