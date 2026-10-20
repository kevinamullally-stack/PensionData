import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
RAW = pf.ssc(adj=False, fixef_k='none', cluster_adj=False)
df = pd.read_pickle('df_newbench_v2.pkl').copy()
# --- tenure at departure and halves, computed over all plan-years of the CIO at the plan (as Stata's bysort cio ppd_id) ---
df['cp']=df.cio.astype(str)+'|'+df.ppd_id.astype(str)
g=df.groupby('cp')
df['last_fy']=g.fy.transform('max'); df['max_ten']=g.cio_tenure.transform('max')
df['ydep']=df.year_departs; df.loc[df.ydep.isna()&(df.curr==0),'ydep']=df.last_fy
df['ten_dep']=df.max_ten+(df.ydep-df.last_fy).clip(lower=0)
ok=df.cio_tenure.notna()&df.ten_dep.notna()&(df.ten_dep>0)
df['second']=np.where(ok,(df.cio_tenure>df.ten_dep/2).astype(float),np.nan)
# --- outcomes ---
df['b_AB']=df.investmentreturn_1yr*100-df.bm_AB
df['fee_ratio_pct']=df.total_fee_pct*100
df['exp_ratio_pct']=df.exp_ratio*100
df['alt_pct']=100*df[['RETotal_Actl','PETotal_Actl','HFTotal_Actl','AltMiscTotal_Actl','COMDTotal_Actl']].sum(axis=1,min_count=5)
df['pe_pct']=100*df.PETotal_Actl; df['hf_pct']=100*df.HFTotal_Actl
df['fye_id']=df.fye1.astype(str)
cls=df[['EQTotal_Fee','FITotal_Fee','RETotal_Fee','PETotal_Fee','HFTotal_Fee']]
df['alt_fee_share']=100*df[['RETotal_Fee','PETotal_Fee','HFTotal_Fee']].sum(axis=1,min_count=3)/cls.sum(axis=1,min_count=5).replace(0,np.nan)
S=df[(df.cio_dum==1)&(df.fy<=2020)&(df.curr1==0)].copy()                   # Table III sample
S['conf']=S.conf_pen_vendor.astype(float)
S['conf_first']=((S.conf==1)&(S.second==0)).astype(float); S['conf_second']=((S.conf==1)&(S.second==1)).astype(float)
S['conf_undef']=((S.conf==1)&S.second.isna()).astype(float)
C=S[(S.conf==1)&(S.curr==0)&S.second.notna()].copy()                      # conflicted CIOs with defined halves
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C5=['l_sib1','wstate_political']
CIOX=['prior_private_exp','Elite_inst']                                  # CIO controls that do not change with tenure
CR=C1+C2+C3+CIOX+C5                                                      # returns and fees
CA=C1+C3+CIOX+C5                                                         # allocation outcomes: no lagged allocations
OUT=[('peer_adj_ret100','Peer-Adjusted Return (%)',CR),('b_AB','Benchmark-Adjusted Return (%)',CR),('fee_ratio_pct','Fee Ratio (%)',CR),('exp_ratio_pct','Expense Ratio (%)',CR),
     ('eqfee100','Equity Fee Rate (%)',CR),('fifee100','Fixed Income Fee Rate (%)',CR),('refee100','Real Estate Fee Rate (%)',CR),('pefee100','Private Equity Fee Rate (%)',CR),('hffee100','Hedge Fund Fee Rate (%)',CR),
     ('alt_fee_share','Alternatives Share of Fees (%)',CR),
     ('alt_pct','Alternatives Allocation (%)',CA),('pe_pct','Private Equity Allocation (%)',CA),('hf_pct','Hedge Fund Allocation (%)',CA)]
def fit(y, rhs, fe, data, combos):
    d=data.dropna(subset=[y]+rhs).copy()
    for _ in range(5):
        n0=len(d)
        for gg in fe.replace(' ','').split('+'): d=d[d[gg].map(d[gg].value_counts())>1]
        if len(d)==n0: break
    d=d.copy(); d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V=(np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov))*(N-1)/(N-K)*G/(G-1)
    w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); out=dict(N=int(N),G=G,adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2),ncio=d.cio.nunique(),nconf=int(d.conf.sum()))
    for nm,wd in combos.items():
        if any(k not in names for k in wd): out[nm]=dict(est=np.nan,se=np.nan,t=np.nan,p=np.nan); continue
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se if se>0 else np.nan
        out[nm]=dict(est=e,se=se,t=t,p=2*stats.t.sf(abs(t),G-1) if se>0 else np.nan)
    return out
R={}
for y,_,ctl in OUT:
    xs=['conf_first','conf_second','conf_undef']
    cmb={'first':{'conf_first':1},'second':{'conf_second':1},'diff':{'conf_second':1,'conf_first':-1}}
    R[('split','fye',y)]=fit(y,xs+ctl,'fye_id',S,cmb)
    R[('split','plan',y)]=fit(y,xs+ctl,'ppd_id + fye_id',S,cmb)
    cm={'second':{'second':1}}
    R[('conf','fye',y)]=fit(y,['second']+ctl,'fye_id',C,cm)
    R[('conf','cio',y)]=fit(y,['second']+ctl,'cp + fye_id',C,cm)
    R[('conf','cio4',y)]=fit(y,['second']+ctl,'cp + fye_id',C[C.ten_dep>=4],cm)
# --- CIO-level paired comparison: average within CIO-year across plans, then within CIO-half ---
PAIR={}
for y,_,_ in OUT:
    P=C.dropna(subset=[y]).groupby(['cio','fy','second'],as_index=False)[y].mean().groupby(['cio','second'])[y].mean().unstack()
    P=P.dropna(); d=P[1.0]-P[0.0]
    PAIR[y]=dict(n=len(d),first=float(P[0.0].mean()),second=float(P[1.0].mean()),diff=float(d.mean()),
                 p_t=float(stats.ttest_rel(P[1.0],P[0.0]).pvalue),p_sr=float(stats.wilcoxon(P[1.0],P[0.0]).pvalue) if len(d)>0 else np.nan,share_up=float((d>0).mean()))
def st(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:7.3f}{st(r['p']):3s}({r['t']:5.2f})"
print('conflicted CIO-years with halves:', len(C), '| CIOs', C.cio.nunique(), '| first/second', int((C.second==0).sum()), int((C.second==1).sum()), '| tenure>=4 CIOs', C[C.ten_dep>=4].cio.nunique())
print('\nA. vs rest of sample (conf_first, conf_second, second-first, p)')
for y,lab,_ in OUT:
    a=R[('split','fye',y)]; b=R[('split','plan',y)]
    print(f"{lab[:30]:30s} FYE: {fm(a['first'])} {fm(a['second'])} diff {fm(a['diff'])} p={a['diff']['p']:.3f} | Plan+FYE diff {fm(b['diff'])} p={b['diff']['p']:.3f} N {a['N']}/{b['N']}")
print('\nB. within conflicted CIOs: Second Half coefficient')
for y,lab,_ in OUT:
    print(f"{lab[:30]:30s} FYE {fm(R[('conf','fye',y)]['second'])} | CIO+FYE {fm(R[('conf','cio',y)]['second'])} | CIO+FYE ten>=4 {fm(R[('conf','cio4',y)]['second'])} | N {R[('conf','fye',y)]['N']}/{R[('conf','cio',y)]['N']}")
print('\nC. CIO-level paired')
for y,lab,_ in OUT:
    p=PAIR[y]; print(f"{lab[:30]:30s} n={p['n']} first {p['first']:.3f} second {p['second']:.3f} diff {p['diff']:.3f} t-test p={p['p_t']:.3f} signrank p={p['p_sr']:.3f} share up {p['share_up']:.2f}")
pd.to_pickle(dict(R=R,PAIR=PAIR,OUT=[(a,b) for a,b,_ in OUT],nC=len(C),nCIO=C.cio.nunique(),n12=(int((C.second==0).sum()),int((C.second==1).sum())),nCIO4=C[C.ten_dep>=4].cio.nunique()),'halves_v3.pkl')
