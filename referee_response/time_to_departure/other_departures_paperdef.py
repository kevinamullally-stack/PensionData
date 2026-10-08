import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_do.pkl')).sort_values(['spell','fy']).copy()
df['fee_ratio_pct'] = df.total_fee_pct*100
S = df[(df.cio_dum==1)&(df.fy<=2020)&(df.curr1==0)].copy()
# departure year (SAS convention), tenure at departure, halves, years to departure
S['last_fy']=S.groupby('spell').fy.transform('max'); S['max_ten']=S.groupby('spell').cio_tenure.transform('max')
S['ydep']=S.year_departs; S.loc[(S.curr==0)&S.ydep.isna(),'ydep']=S.last_fy
S['ten_dep']=S.max_ten+(S.ydep-S.last_fy).clip(lower=0)
S['ttd']=S.fy-S.ydep
S['ever_any'] = ((S.ever_retire.fillna(0)+S.ever_leave_pub.fillna(0)+S.ever_die.fillna(0)+S.priv_nonam_job.fillna(0))>0).astype(int)
S['conf'] = ((S.conf_pen_vendor==1)&(S.curr==0)).astype(int)
S['other'] = ((S.conf_pen_vendor==0)&(S.curr==0)&(S.ever_any==1)).astype(int)           # classified other departures (Table IV placebo types)
S['other_all'] = ((S.conf_pen_vendor==0)&(S.curr==0)).astype(int)                      # any non-conflicted departed CIO
S['second'] = np.where((S.curr==0)&S.ten_dep.notna()&(S.ten_dep>0)&S.cio_tenure.notna(), (S.cio_tenure>S.ten_dep/2).astype(float), np.nan)
for grp in ['conf','other','other_all']: S[f'{grp}_second'] = S[grp]*S.second
BINS=['m5','m4','m3','m2','m1','p0']
def binlab(t):
    if pd.isna(t): return 'na'
    return 'm5' if t<=-5 else {-4:'m4',-3:'m3',-2:'m2',-1:'m1',0:'p0'}.get(int(t),'na')
S['bin']=S.ttd.apply(binlab)
for grp in ['conf','other']:
    for b in BINS: S[f'{grp}_{b}'] = ((S[grp]==1)&(S['bin']==b)).astype(int)
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
def fit(y, rhs, fe, d): return pf.feols(f'{y} ~ {" + ".join(rhs)} | {fe}', data=d, vcov={'CRV1':'ppd_id + fy'})
def psd(m):
    V=np.asarray(m._vcov); w,Q=np.linalg.eigh((V+V.T)/2); return (Q*np.clip(w,0,None))@Q.T
def lc(m, w):
    names=list(m._coefnames); b=np.asarray(m._beta_hat); V=psd(m); c=np.zeros(len(names))
    for k,v in w.items():
        if k not in names: return (np.nan,np.nan,np.nan)
        c[names.index(k)]=v
    e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); G=min(m._G); p=2*stats.t.sf(abs(e/se),G-1) if se>0 else np.nan; return e,se,p
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f3(e,se,p): return "   n/a" if np.isnan(e) else f"{e:7.3f}{star(p):3s}({e/se:5.2f})"
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("# Other-departure comparison, paper definitions: Conflicted = conf_pen_vendor, sample cio_dum==1 & fy<=2020 & curr1==0, do-file controls, SE double clustered by plan and year (t-stats in parentheses)")
H = S[S.second.notna() & ((S.conf==1)|(S.other==1))]
P(f"\nHalves sample: {len(H)} CIO-years | conflicted CIOs {H[H.conf==1].cio.nunique()} ({(H.conf==1).sum()} yrs) | other classified departures {H[H.other==1].cio.nunique()} CIOs ({(H.other==1).sum()} yrs)")
P("other departure types (CIO-years, non-exclusive): retire", int(H[H.other==1].ever_retire.sum()), "| leave public", int(H[H.other==1].ever_leave_pub.sum()), "| private non-vendor", int(H[H.other==1].priv_nonam_job.sum()), "| die", int(H[H.other==1].ever_die.sum()))
P("\n## 1. Second half minus first half: conflicted vs other departures (reference = first half of each group; 'Conflicted' row = conflicted first-half level vs other departers' first half)")
SPECS=[('(1) Year FE, base controls',C1+C2+C3,'fy'),('(2) Year FE, all controls',C1+C2+C3+C4+C5,'fy'),('(4) Plan + Year FE',C1+C2+C3+C4+C5,'ppd_id + fy'),('(5) CIO FE + Year FE',C1+C2+C3,'spell + fy')]
for y,lab in [('peer_adj_ret100','Peer-adjusted return'),('bench_adj_ret_pct','Benchmark-adjusted return'),('fee_ratio_pct','Fee ratio')]:
    P(f"\n### {lab}")
    P(f"{'spec':30s} {'Conf level (1st half)':24s} {'Conf 2nd-1st':24s} {'Other 2nd-1st':24s} {'Difference':24s} N")
    for name,ctrl,fe in SPECS:
        rhs = (['conf'] if not fe.startswith('spell') else []) + ['conf_second','other_second'] + ctrl
        m = fit(y, rhs, fe, H)
        P(f"{name:30s} {f3(*lc(m,{'conf':1})) if 'conf' in m._coefnames else '   absorbed':24s} {f3(*lc(m,{'conf_second':1})):24s} {f3(*lc(m,{'other_second':1})):24s} {f3(*lc(m,{'conf_second':1,'other_second':-1})):24s} {m._N}")
    # robustness: all non-conflicted departed CIOs as comparison
    H2 = S[S.second.notna() & ((S.conf==1)|(S.other_all==1))]
    m = fit(y, ['conf','conf_second','other_all_second']+C1+C2+C3+C4+C5, 'ppd_id + fy', H2)
    P(f"{'(4) vs ALL non-conf departers':30s} {f3(*lc(m,{'conf':1})):24s} {f3(*lc(m,{'conf_second':1})):24s} {f3(*lc(m,{'other_all_second':1})):24s} {f3(*lc(m,{'conf_second':1,'other_all_second':-1})):24s} {m._N}")
P("\n## 2. Years-to-departure bins. Pooled: reference = non-departing CIO-years in the curr1==0 sample (long-tenured current CIOs) and unclassified exits. Within CIO: relative to own <=-5 years.")
B = S.copy()
for y,lab in [('peer_adj_ret100','Peer-adjusted return'),('bench_adj_ret_pct','Benchmark-adjusted return')]:
    for fe,ctrl,rel,title in [('ppd_id + fy',C1+C2+C3+C4+C5,False,'Pooled, plan + year FE'),('spell + fy',C1+C2+C3,True,'Within CIO, CIO + year FE')]:
        use = BINS[1:] if rel else BINS
        m = fit(y, [f'conf_{b}' for b in use]+[f'other_{b}' for b in use]+ctrl, fe, B)
        P(f"\n### {lab} | {title} | N={m._N}" + ("  [relative to own <=-5 bin]" if rel else ""))
        P(f"{'bin':6s} {'Conflicted':24s} {'Other departure':24s} {'Difference':24s}")
        for b in use: P(f"{b:6s} {f3(*lc(m,{f'conf_{b}':1})):24s} {f3(*lc(m,{f'other_{b}':1})):24s} {f3(*lc(m,{f'conf_{b}':1,f'other_{b}':-1})):24s}")
        near={f'conf_{b}':1/3 for b in ['m2','m1','p0']}; onear={f'other_{b}':1/3 for b in ['m2','m1','p0']}
        far = {'conf_m4':-.5,'conf_m5':-.5} if not rel else {'conf_m4':-.5}; ofar = {'other_m4':-.5,'other_m5':-.5} if not rel else {'other_m4':-.5}
        if rel: far={'conf_m4':-0.5}; ofar={'other_m4':-0.5}   # far = avg of (<=-5 → 0 by normalisation) and -4
        nf = lc(m,{**near,**far}); onf = lc(m,{**onear,**ofar}); dd = lc(m,{**near,**far,**{k:-v for k,v in onear.items()},**{k:-v for k,v in ofar.items()}})
        P(f"  Near(-2..0) - Far(<=-4): conflicted {f3(*nf)} | other {f3(*onf)} | DiD {f3(*dd)}")
P("\n## 3. Near (-1,0) minus far (<=-4) by departure type, pooled plan + year FE, all controls, peer-adjusted")
T = S.copy(); T['typ']=np.select([T.conf==1,(T.other==1)&(T.ever_retire==1),(T.other==1)&(T.ever_leave_pub==1),(T.other==1)&(T.priv_nonam_job==1)],['conf','retire','public','privnonam'],default='none')
terms=[]
for t in ['conf','retire','public','privnonam']:
    for b,cond in [('far',T.ttd<=-4),('mid',T.ttd.isin([-3,-2])),('near',T.ttd>=-1)]:
        T[f'{t}_{b}']=((T.typ==t)&cond).astype(int); terms.append(f'{t}_{b}')
for y,lab in [('peer_adj_ret100','Peer-adjusted'),('bench_adj_ret_pct','Benchmark-adjusted')]:
    m = fit(y, terms+C1+C2+C3+C4+C5, 'ppd_id + fy', T)
    P(f"\n{lab} N={m._N}: counts " + str({t:int((T.typ==t).sum()) for t in ['conf','retire','public','privnonam']}))
    for t in ['conf','retire','public','privnonam']:
        row = f"  {t:10s} far {f3(*lc(m,{f'{t}_far':1})):22s} near {f3(*lc(m,{f'{t}_near':1})):22s} near-far {f3(*lc(m,{f'{t}_near':1,f'{t}_far':-1})):22s}"
        if t!='conf': row += f" conf minus {t}: {f3(*lc(m,{'conf_near':1,'conf_far':-1,f'{t}_near':-1,f'{t}_far':1}))}"
        P(row)
open('/home/user/PensionData/referee_response/time_to_departure/results_other_departures_paperdef.md','w').write('\n'.join(out))
