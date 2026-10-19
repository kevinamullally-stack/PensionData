exec(open('xsec_setup_v2.py').read())          # S = Table III sample (b_AB = updated benchmark-adjusted return), C1-C3, RAW
CTL=C1+C2+C3+['l_log_cio_age','l_log_cio_tenure','l_sib1','wstate_political']   # do-file globals at Table 5 / 5b
YS=[('peer_adj_ret100','Peer-adjusted return'),('b_AB','Benchmark-adjusted return (updated benchmark)')]
S['conf']=S.conf_pen_vendor.astype(float); S['shock']=S.shock2.astype(float); S['confxshock']=S.conf*S.shock
S['ever_any']=(S.ever_retire.fillna(0)+S.ever_leave_pub.fillna(0)+S.ever_die.fillna(0)+S.priv_nonam_job.fillna(0)).clip(upper=1)
S['other_job']=(S.ever_leave_pub.fillna(0)+S.priv_nonam_job.fillna(0)).clip(upper=1)
for nm,v in [('oth_any','ever_any'),('oth_ret','ever_retire'),('oth_job','other_job')]:
    S[nm]=((S[v]==1)&(S.conf==0)).astype(float); S[nm+'xshock']=S[nm]*S.shock

def fit(y, rhs, fe, combos=None, walds=None, data=None):
    d=(S if data is None else data).dropna(subset=[y]+rhs).copy()
    for _ in range(5):
        n0=len(d)
        for g in fe.replace(' ','').split('+'): d=d[d[g].map(d[g].value_counts())>1]
        if len(d)==n0: break
    d=d.copy(); d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V=(np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov))*(N-1)/(N-K)*G/(G-1)
    w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); tc=stats.t.ppf(0.975,G-1)
    out=dict(N=int(N),G=G,adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2),nconf=int(d.conf.sum()) if 'conf' in d else None)
    for nm,wd in (combos or {}).items():
        if any(k not in names for k in wd): out[nm]=dict(est=np.nan,se=np.nan,t=np.nan,p=np.nan,lo=np.nan,hi=np.nan); continue
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se if se>0 else np.nan
        out[nm]=dict(est=e,se=se,t=t,p=2*stats.t.sf(abs(t),G-1) if se>0 else np.nan,lo=e-tc*se,hi=e+tc*se)
    for nm,vs in (walds or {}).items():
        vs=[v for v in vs if v in names]; ix=[names.index(v) for v in vs]
        bb=b[ix]; VV=V[np.ix_(ix,ix)]; Fst=float(bb@np.linalg.pinv(VV)@bb)/len(ix)
        out[nm]=dict(F=Fst,p=float(stats.f.sf(Fst,len(ix),G-1)),q=len(ix))
    return out
FES=[('fy','Year FE'),('ppd_id','Plan FE'),('ppd_id + fy','Plan and year FE')]
R={}
# ---------- A. Table VIII ----------
for y,_ in YS:
    for fe,_ in FES:
        R[('t3',y,fe)]=fit(y,['conf']+CTL,fe,{'conf':{'conf':1}})
        R[('t8',y,fe)]=fit(y,['conf','confxshock','shock']+CTL,fe,{'conf':{'conf':1},'cxs':{'confxshock':1},'in':{'conf':1,'confxshock':1}})
# ---------- B. event study, FY2008 base, Conflicted main effect ----------
BASE=2008; YRS=[t for t in range(2005,2018) if t!=BASE]
S['es_pre']=S.conf*(S.fy<2005); S['es_post']=S.conf*(S.fy>2017)
for t in YRS: S[f'es_{t}']=S.conf*(S.fy==t)
EVB=['es_pre']+[f'es_{t}' for t in YRS]+['es_post']
PRE_B=['es_pre']+[f'es_{t}' for t in YRS if t<2009]; WIN_B=[f'es_{t}' for t in range(2009,2014)]; POST_B=[f'es_{t}' for t in YRS if t>2013]+['es_post']
for y,_ in YS:
    for fe,_ in FES:
        cmb={v:{v:1} for v in EVB}; cmb['conf']={'conf':1}
        cmb['win_mean']={v:1/len(WIN_B) for v in WIN_B}
        pm=[f'es_{t}' for t in range(2014,2018)]; cmb['post_mean']={v:1/len(pm) for v in pm}
        cmb['return']={**{v:1/len(pm) for v in pm},**{v:-1/len(WIN_B) for v in WIN_B}}
        R[('es',y,fe)]=fit(y,['conf']+EVB+CTL,fe,cmb,{'pre':PRE_B,'win':WIN_B,'post':POST_B})
# ---------- C. event study, two-year bins, reference FY2007-08 ----------
BINS=[('b0102',2001,2002),('b0304',2003,2004),('b0506',2005,2006),('b0910',2009,2010),('b1113',2011,2013),('b1415',2014,2015),('b1617',2016,2017),('b1820',2018,2020)]
for nm,a,z in BINS: S[nm]=S.conf*S.fy.between(a,z)
BV=[b[0] for b in BINS]; PRE_C=['b0102','b0304','b0506']; WIN_C=['b0910','b1113']; POST_C=['b1415','b1617','b1820']
for y,_ in YS:
    for fe,_ in FES:
        cmb={v:{v:1} for v in BV}; cmb['conf']={'conf':1}
        R[('bins',y,fe)]=fit(y,['conf']+BV+CTL,fe,cmb,{'pre':PRE_C,'win':WIN_C,'post':POST_C})
# ---------- D. differential exposure ----------
ALLOC=C2
for a in ALLOC: S[f'{a}xshock']=S[a]*S.shock
YRS_ALL=sorted(S.fy.unique())[1:]           # interactions with every fiscal year except the first
for a in ALLOC:
    for t in YRS_ALL: S[f'{a}_y{t}']=S[a]*(S.fy==t)
EXPO=[('base','Table VIII as estimated',[]),
      ('pe_s','+ Lagged PE share x Shock Period',['l_pexshock']),
      ('all_s','+ All lagged allocations x Shock Period',[f'{a}xshock' for a in ALLOC]),
      ('pe_y','+ Lagged PE share x fiscal-year indicators',[f'l_pe_y{t}' for t in YRS_ALL]),
      ('all_y','+ All lagged allocations x fiscal-year indicators',[f'{a}_y{t}' for a in ALLOC for t in YRS_ALL])]
for y,_ in YS:
    for fe in ['fy','ppd_id + fy']:
        for k,_,extra in EXPO:
            R[('expo',k,y,fe)]=fit(y,['conf','confxshock','shock']+CTL+extra,fe,{'conf':{'conf':1},'cxs':{'confxshock':1},'in':{'conf':1,'confxshock':1}})
PEMEAN={g:float(S.loc[S.conf==g,'l_pe'].mean()) for g in [0,1]}
PEMEAN_W={g:float(S.loc[(S.conf==g)&(S.shock==1),'l_pe'].mean()) for g in [0,1]}
# ---------- E. placebo windows ----------
STARTS=list(range(2002,2017))
for s in STARTS:
    S['W']=S.fy.between(s,s+4).astype(float); S['confxW']=S.conf*S.W
    for y,_ in YS:
        for fe in ['fy','ppd_id + fy']:
            R[('roll',s,y,fe)]=fit(y,['conf','confxW','W']+CTL,fe,{'cxw':{'confxW':1},'conf':{'conf':1}})
PRE_S=S[S.fy<=2008].copy(); PRE_S['F']=(PRE_S.fy>=2005).astype(float); PRE_S['confxF']=PRE_S.conf*PRE_S.F
for y,_ in YS:
    for fe in ['fy','ppd_id + fy']:
        R[('prefake',y,fe)]=fit(y,['conf','confxF','F']+CTL,fe,{'cxf':{'confxF':1},'conf':{'conf':1}},data=PRE_S)
# ---------- F. placebo groups ----------
GRP=[('oth_any','Any other departure'),('oth_ret','Retirement'),('oth_job','Other job (public plan or non-asset-manager firm)')]
for g,_ in GRP:
    for y,_ in YS:
        for fe in ['fy','ppd_id + fy']:
            R[('grp',g,y,fe)]=fit(y,['conf','confxshock',g,g+'xshock','shock']+CTL,fe,
                                  {'conf':{'conf':1},'cxs':{'confxshock':1},'oth':{g:1},'oxs':{g+'xshock':1},'diff':{'confxshock':1,g+'xshock':-1}})
pd.to_pickle(dict(R=R,YS=YS,FES=FES,EVB=EVB,YRS=YRS,BASE=BASE,BINS=BINS,EXPO=[(a,b) for a,b,_ in EXPO],STARTS=STARTS,GRP=GRP,PEMEAN=PEMEAN,PEMEAN_W=PEMEAN_W),'shock_tests.pkl')
# ---------- print ----------
def st(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
for y,yl in YS:
    print(f"\n######## {yl}")
    print("A. Table VIII  [full-sample conf | conf outside window | conf x shock | effect in window]")
    for fe,fl in FES: print(f"  {fl:18s} {fm(R[('t3',y,fe)]['conf'])} | {fm(R[('t8',y,fe)]['conf'])} | {fm(R[('t8',y,fe)]['cxs'])} | {fm(R[('t8',y,fe)]['in'])}  N {R[('t8',y,fe)]['N']}")
    print("B. Event study FY2008 base (plan+year FE shown first)")
    for fe,fl in [FES[2],FES[0]]:
        r=R[('es',y,fe)]
        print(f"  {fl}: conf(2008 gap) {fm(r['conf'])}")
        print("   "+' '.join(f"{v[3:]}:{r[v]['est']:.2f}({r[v]['t']:.1f})" for v in EVB))
        print(f"   pre=0 p {r['pre']['p']:.3f} | window=0 p {r['win']['p']:.3f} | post=0 p {r['post']['p']:.3f} | window mean {fm(r['win_mean'])} | post mean {fm(r['post_mean'])} | post-window {fm(r['return'])}")
    print("C. Two-year bins, ref FY2007-08")
    for fe,fl in [FES[2],FES[0]]:
        r=R[('bins',y,fe)]
        print(f"  {fl}: "+' '.join(f"{v}:{r[v]['est']:.2f}({r[v]['t']:.1f})" for v in [b[0] for b in BINS])+f" | pre p {r['pre']['p']:.3f} win p {r['win']['p']:.3f} post p {r['post']['p']:.3f}")
    print("D. Exposure: conf x shock")
    for fe in ['fy','ppd_id + fy']: print(f"  {fe:12s} "+' | '.join(f"{k}: {fm(R[('expo',k,y,fe)]['cxs'])}" for k,_,_ in EXPO))
    print("E. Rolling windows conf x W (plan+year FE / year FE)")
    for s in STARTS: print(f"  {s}-{s+4}: {fm(R[('roll',s,y,'ppd_id + fy')]['cxw'])} | {fm(R[('roll',s,y,'fy')]['cxw'])}")
    print(f"  pre-period fake window 2005-08 (sample fy<=2008): plan+year {fm(R[('prefake',y,'ppd_id + fy')]['cxf'])} | year {fm(R[('prefake',y,'fy')]['cxf'])}")
    print("F. Placebo groups (plan+year FE / year FE): conf x shock | other x shock | difference")
    for g,gl in GRP:
        for fe in ['ppd_id + fy','fy']:
            r=R[('grp',g,y,fe)]; print(f"  {gl[:22]:22s} {fe:12s} {fm(r['cxs'])} | {fm(r['oxs'])} | {fm(r['diff'])}")
print('\nlagged PE share: all years', {k:round(v,2) for k,v in PEMEAN.items()}, '| shock window', {k:round(v,2) for k,v in PEMEAN_W.items()})
