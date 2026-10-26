exec(open('table3_conflicted_halves_fye1.py').read().split("RES={(v,y)")[0])     # S (Table III sample) with halves; run(); controls; RAW
import time, os
import statsmodels.api as sm
# ---------------- variables ----------------
S['fee']=100*S.total_fee_pct                                                                  # Fee Ratio (%)
S['alt']=100*S[['RETotal_Actl','PETotal_Actl','HFTotal_Actl','AltMiscTotal_Actl','COMDTotal_Actl']].sum(axis=1,min_count=5)   # alternatives share (%)
S['fslope']=S.slope_fee_pct_controls                                                         # authors' Fee Slope (CIO-plan level)
lo,hi=S.fslope.quantile([.01,.99]); S['fslope_w']=S.fslope.clip(lo,hi)
FULL=C1+C2+C3+C4+C5; NOALLOC=C1+C3+C4+C5
def tw(y,rhs,fe,dat,combos):    # two-way (plan, year) clustered estimates, as in the Table III replications
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={cl:pf.feols(f,data=dat,vcov={'CRV1':cl},ssc=RAW) for cl in ['ppd_id','fy','py']}
    m=fits['ppd_id']; names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V=(np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['py']._vcov))*(N-1)/(N-K)*G/(G-1)
    w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); out=dict(N=int(N),G=G,adjr2=float(pf.feols(f,data=dat,vcov='iid')._adj_r2),coef={})
    for n in names:
        i=names.index(n); se=np.sqrt(max(V[i,i],0)); out['coef'][n]=(float(b[i]),float(se),float(2*stats.t.sf(abs(b[i]/se),G-1)) if se>0 else np.nan)
    for nm,wd in combos.items():
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); out[nm]=(e,se,float(2*stats.t.sf(abs(e/se),G-1)))
    return out
YS=[('peer_adj_ret100','Peer-Adjusted Return'),('b_AB','Benchmark-Adjusted Return')]
FES={'fye':'fye_id','plan':'ppd_id + fye_id'}
MCOLS=[('noalloc','No allocation controls',NOALLOC),('t3','Table III controls',FULL),('fee','+ Fee Ratio',FULL+['fee']),('fslope','+ Fee Slope',FULL+['fslope']),
       ('alt','+ Alternatives share',FULL+['alt']),('all','+ All three',FULL+['fee','fslope','alt'])]
MED={}; MSAMP={}
for y,_ in YS:
    d=S.dropna(subset=[y]+FULL+['fee','fslope','alt']).copy()                                 # common mediation sample
    for fk,fe in FES.items():
        d2=d.copy()
        for _ in range(10):                                                                       # drop singleton FE groups once, so every column uses the same rows
            n0=len(d2)
            for g_ in fe.replace(' ','').split('+'): d2=d2[d2[g_].map(d2[g_].value_counts())>1]
            if len(d2)==n0: break
        MSAMP[(y,fk)]=d2
        for ck,_,rhs in MCOLS: MED[(y,fk,ck)]=tw(y,['conf_pen_vendor']+rhs,fe,d2,{})
        # path a: does Conflicted predict the mediator (same sample, same controls; alternatives share without allocation controls)
        for med in ['fee','fslope','alt']: MED[(y,fk,'a_'+med)]=tw(med,['conf_pen_vendor']+(NOALLOC if med=='alt' else FULL),fe,d2,{})
        MED[(y,fk,'fslope_w')]=tw(y,['conf_pen_vendor']+FULL+['fslope_w'],fe,d2,{})
# ---------------- plan-block bootstrap of the change in the Conflicted coefficient ----------------
B=500; rng=np.random.default_rng(20261026); BOOT={}
t0=time.time()
if os.path.exists('mechanism_mediation_boot.pkl'): BOOT=pd.read_pickle('mechanism_mediation_boot.pkl')
for y,_ in YS:
    for fk,fe in FES.items():
        if (y,fk) in BOOT: continue
        d=MSAMP[(y,fk)]; plans=d.ppd_id.unique(); blocks={p:g for p,g in d.groupby('ppd_id')}; draws=[]
        for b in range(B):
            pick=rng.choice(plans,len(plans),replace=True)
            db=pd.concat([blocks[p].assign(pid_b=i) for i,p in enumerate(pick)],ignore_index=True)
            feb=fe.replace('ppd_id','pid_b'); row={}
            try:
                for ck,_,rhs in MCOLS:
                    m=pf.feols(f"{y} ~ conf_pen_vendor + {' + '.join(rhs)} | {feb}",data=db,vcov='iid'); row[ck]=float(m.coef()['conf_pen_vendor'])
                draws.append(row)
            except Exception as e: pass
        BOOT[(y,fk)]=pd.DataFrame(draws)
        print(f"bootstrap {y} {fk}: {len(draws)} draws, {time.time()-t0:.0f}s", flush=True)
        pd.to_pickle(BOOT,'mechanism_mediation_boot.pkl')
def bstat(y,fk,ck,ref='t3'):
    D_=BOOT[(y,fk)]; dif=D_[ref]-D_[ck]; pt=MED[(y,fk,ref)]['coef']['conf_pen_vendor'][0]-MED[(y,fk,ck)]['coef']['conf_pen_vendor'][0]
    se=dif.std(); return dict(diff=pt,se=se,p=float(2*stats.norm.sf(abs(pt/se))),lo=float(dif.quantile(.025)),hi=float(dif.quantile(.975)))
CH={(y,fk,ck):bstat(y,fk,ck) for y,_ in YS for fk in FES for ck,_,_ in MCOLS if ck!='t3'}
# ---------------- timing: halves split (Table III controls; allocation outcome without allocation controls) ----------------
OUTS=[('peer_adj_ret100','Peer-Adjusted Return',FULL),('b_AB','Benchmark-Adjusted Return',FULL),('fee','Fee Ratio (%)',FULL),('alt','Alternatives share (%)',NOALLOC)]
LEV={}; HALF={}
for y,_,ctl in OUTS:
    for fk,fe in FES.items():
        LEV[(y,fk)]=tw(y,['conf_pen_vendor']+ctl,fe,S.dropna(subset=[y]+ctl),{})
        xs=['conf_pen_vendor_h1','conf_pen_vendor_h2','conf_pen_vendor_hu']
        dd=S.dropna(subset=[y]+ctl)
        if dd.conf_pen_vendor_hu.sum()==0: xs=xs[:2]
        HALF[(y,fk)]=tw(y,xs+ctl,fe,dd,{'h1':{'conf_pen_vendor_h1':1},'h2':{'conf_pen_vendor_h2':1},'diff':{'conf_pen_vendor_h2':1,'conf_pen_vendor_h1':-1}})
# Fee Slope level difference at the CIO-plan level (one observation per CIO-plan, as the variable is defined)
sp=S.dropna(subset=['fslope']).groupby('cp').agg(fs=('fslope','first'),conf=('conf_pen_vendor','max'),ppd_id=('ppd_id','first'))
m=sm.OLS(sp.fs,sm.add_constant(sp.conf)).fit(cov_type='cluster',cov_kwds={'groups':sp.ppd_id})
FSL=dict(c=sp[sp.conf==1].fs.mean(),o=sp[sp.conf==0].fs.mean(),medc=sp[sp.conf==1].fs.median(),medo=sp[sp.conf==0].fs.median(),diff=m.params['conf'],p=m.pvalues['conf'],
         prs=stats.mannwhitneyu(sp[sp.conf==1].fs,sp[sp.conf==0].fs).pvalue,nc=int((sp.conf==1).sum()),no=int((sp.conf==0).sum()))
# ---------------- timing: equal-weighted within-CIO halves change with CIO + FYE FE (departed CIOs) ----------------
exec(open('returns_halves_equal_weight_fe.py').read().split("D['conf']=D.groupby")[0].split("YS=[('peer_adj_ret100'")[1].split("\n",1)[1])   # fitw()
Dd=S[(S.curr==0)&S.second.notna()].copy(); Dd['conf']=Dd.groupby('cp').conf_pen_vendor.transform('max'); Dd['conf_second']=Dd.conf*Dd.second
EW={y:fitw(y,['second','conf_second'],'cp + fye_id',Dd,{'oth':{'second':1},'cnf':{'second':1,'conf_second':1},'diff':{'conf_second':1}}) for y,_,_ in OUTS}
pd.to_pickle(dict(MED=MED,CH=CH,LEV=LEV,HALF=HALF,EW=EW,FSL=FSL,YS=YS,OUTS=[(a,b) for a,b,_ in OUTS],MCOLS=[(a,b) for a,b,_ in MCOLS],B=B,
                  NMS={k:(len(v),int(v.conf_pen_vendor.sum()),v[v.conf_pen_vendor==1].cio.nunique()) for k,v in MSAMP.items()}),'mechanism_mediation.pkl')
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
for y,yl in YS:
    for fk in FES:
        print(f"\n## Mediation | {yl} | {fk} | N {MED[(y,fk,'t3')]['N']}")
        for ck,lab,_ in MCOLS:
            c=MED[(y,fk,ck)]['coef']; b,se,p=c['conf_pen_vendor']
            meds=' '.join(f"{v} {c[v][0]:+.3f}{st(c[v][2])}" for v in ['fee','fslope','alt'] if v in c)
            ch=CH.get((y,fk,ck)); chs=f" | change vs T3 {ch['diff']:+.3f} (boot p {ch['p']:.2f}, 95% [{ch['lo']:+.2f},{ch['hi']:+.2f}])" if ch else ''
            print(f"  {lab:24s} Conf {b:+.3f}{st(p)} (t {b/se:.2f}) {meds}{chs}")
        for med in ['fee','fslope','alt']:
            b,se,p=MED[(y,fk,'a_'+med)]['coef']['conf_pen_vendor']; print(f"  path a: {med:6s} on Conflicted {b:+.4f}{st(p)} (t {b/se:.2f})")
        b,se,p=MED[(y,fk,'fslope_w')]['coef']['conf_pen_vendor']; print(f"  + winsorized Fee Slope: Conf {b:+.3f}{st(p)}")
print("\n## Levels and halves (Table III controls)")
for y,yl,_ in OUTS:
    for fk in FES:
        L_=LEV[(y,fk)]['coef']['conf_pen_vendor']; H=HALF[(y,fk)]
        print(f"  {yl:26s} {fk:5s} Conflicted {L_[0]:+.3f}{st(L_[2])} | first {H['h1'][0]:+.3f}{st(H['h1'][2])} second {H['h2'][0]:+.3f}{st(H['h2'][2])} diff {H['diff'][0]:+.3f} (p {H['diff'][2]:.3f})")
    e=EW[y]; print(f"  {'':26s} EW CIO+FYE FE: conflicted {e['cnf']['est']:+.3f} (p {e['cnf']['p']:.3f}) other {e['oth']['est']:+.3f} diff {e['diff']['est']:+.3f} (p {e['diff']['p']:.3f}; plan p {e['diff']['pp']:.3f})")
print(f"\nFee Slope by CIO-plan: conflicted {FSL['c']:+.4f} (median {FSL['medc']:+.4f}) other {FSL['o']:+.4f} (median {FSL['medo']:+.4f}) diff {FSL['diff']:+.4f} p {FSL['p']:.3f} rank p {FSL['prs']:.3f} n {FSL['nc']}/{FSL['no']}")
