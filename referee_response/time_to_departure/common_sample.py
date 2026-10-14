import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_do.pkl')).sort_values(['spell','fy']).copy()
S = df[(df.cio_dum==1)&(df.fy<=2020)&(df.curr1==0)].copy()
S['last_fy']=S.groupby('spell').fy.transform('max'); S['max_ten']=S.groupby('spell').cio_tenure.transform('max')
S['ydep']=S.year_departs; S.loc[(S.curr==0)&S.ydep.isna(),'ydep']=S.last_fy
S['ten_dep']=S.max_ten+(S.ydep-S.last_fy).clip(lower=0)
ok=(S.curr==0)&S.ten_dep.notna()&(S.ten_dep>0)&S.cio_tenure.notna()
S['second']=np.where(ok,(S.cio_tenure>S.ten_dep/2).astype(float),np.nan)
S['conf']=S.conf_pen_vendor.astype(int)
S['conf_first']=((S.conf==1)&(S.second==0)).astype(int); S['conf_second']=((S.conf==1)&(S.second==1)).astype(int); S['conf_undef']=((S.conf==1)&S.second.isna()).astype(int)
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
ALL=C1+C2+C3+C4+C5
COMMON = S[S.peer_adj_ret100.notna() & S.bench_adj_ret_pct.notna()].copy()
print(f"Table III sample: {len(S)} plan-years, {S.ppd_id.nunique()} plans | common sample (both returns): {len(COMMON)} plan-years, {COMMON.ppd_id.nunique()} plans | conflicted plan-years: {int(S.conf.sum())} -> {int(COMMON.conf.sum())} | conflicted CIOs: {S[S.conf==1].cio.nunique()} -> {COMMON[COMMON.conf==1].cio.nunique()}")
print("peer-adj in Table III sample vs common: mean %.3f vs %.3f ; conflicted mean %.3f vs %.3f" % (S.peer_adj_ret100.mean(), COMMON.peer_adj_ret100.mean(), S[S.conf==1].peer_adj_ret100.mean(), COMMON[COMMON.conf==1].peer_adj_ret100.mean()))
def psd_t(m, w):
    V=np.asarray(m._vcov); e,Q=np.linalg.eigh((V+V.T)/2); V=(Q*np.clip(e,0,None))@Q.T; names=list(m._coefnames); b=np.asarray(m._beta_hat); c=np.zeros(len(names))
    for k,v in w.items():
        if k not in names: return (np.nan,np.nan,np.nan)
        c[names.index(k)]=v
    est=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=est/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),min(m._G)-1) if se>0 else np.nan; return est,t,p
def fit(y,rhs,fe,d): return pf.feols(f'{y} ~ {" + ".join(rhs)} | {fe}', data=d, vcov={'CRV1':'ppd_id + fy'})
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f(e,t,p): return "    n/a" if np.isnan(e) else f"{e:7.3f}{star(p):3s}({t:5.2f})"
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("\n# COMMON SAMPLE (both peer- and benchmark-adjusted returns non-missing). Paper spec; SE double clustered by plan & year; t in parentheses.")
P("\n## A. Table III baseline, Conflicted CIO coefficient, common sample")
SPECS=[('(1) Year FE, base',C1+C2+C3,'fy'),('(2) Year FE, all',ALL,'fy'),('(3) Plan FE',ALL,'ppd_id'),('(4) Plan+Year FE',ALL,'ppd_id + fy')]
for y,lab in [('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj')]:
    P(f"  {lab:10s} " + " | ".join(f"{n}: {f(*psd_t(fit(y,['conf']+c,fe,COMMON),{'conf':1}))} N={fit(y,['conf']+c,fe,COMMON)._N}" for n,c,fe in SPECS))
P("\n## B. Full-sample split (Table XI-split design) on the common sample")
P(f"{'':12s}{'':22s}{'(1) Year FE, base':28s}{'(2) Year FE, all':28s}{'(3) Plan FE':28s}{'(4) Plan+Year FE':28s}")
for y,lab in [('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj')]:
    res=[fit(y,['conf_first','conf_second','conf_undef']+c,fe,COMMON) for n,c,fe in SPECS]
    P(f"{lab:12s}{'First half':22s}" + "".join(f"{f(*psd_t(m,{'conf_first':1})):28s}" for m in res))
    P(f"{'':12s}{'Second half':22s}" + "".join(f"{f(*psd_t(m,{'conf_second':1})):28s}" for m in res))
    P(f"{'':12s}{'p: first = second':22s}" + "".join(f"{psd_t(m,{'conf_second':1,'conf_first':-1})[2]:<28.3f}" for m in res))
    P(f"{'':12s}{'N / adj R2':22s}" + "".join(f"{m._N} / {m._adj_r2:.3f}{'':14s}" for m in res))
P("\n## C. Conflicted-only (Table XI design) on the common sample")
CC = COMMON[(COMMON.conf==1)&ok.reindex(COMMON.index).fillna(False)]
COLS=[('(1) Year FE, base',C1+C2+C3,'fy'),('(2) Year FE, all',ALL,'fy'),('(3) Plan FE',ALL,'ppd_id'),('(4) Plan+Year FE',ALL,'ppd_id + fy'),('(5) CIO FE',C1+C2+C3,'spell + fy'),('(6) CIO FE, ten>=4',C1+C2+C3,'spell + fy')]
P(f"conflicted-only common sample: {len(CC)} CIO-years, {CC.cio.nunique()} CIOs")
for y,lab in [('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj')]:
    row=[]
    for n,c,fe in COLS:
        d = CC if 'ten>=4' not in n else CC[CC.ten_dep>=4]
        m=fit(y,['second']+c,fe,d); row.append(f"{n}: {f(*psd_t(m,{'second':1}))} N={m._N}")
    P(f"  {lab:10s} " + " | ".join(row))
P("\n## D. Same regressions, no controls (to separate sample from control effects), common sample")
for y,lab in [('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj')]:
    m1=fit(y,['conf_first','conf_second','conf_undef'],'fy',COMMON); m2=fit(y,['conf_first','conf_second','conf_undef'],'ppd_id + fy',COMMON); m3=fit(y,['second'],'spell + fy',CC)
    P(f"  {lab:10s} split yearFE: 1st {f(*psd_t(m1,{'conf_first':1}))} 2nd {f(*psd_t(m1,{'conf_second':1}))} | split plan+yr: 1st {f(*psd_t(m2,{'conf_first':1}))} 2nd {f(*psd_t(m2,{'conf_second':1}))} | within-CIO: {f(*psd_t(m3,{'second':1}))}")
P("\n## E. Correlation of the two measures in the common sample")
P("  corr(peer-adj, bench-adj) all: %.3f | conflicted only: %.3f | within plan-year demeaned by year: %.3f" % (COMMON[['peer_adj_ret100','bench_adj_ret_pct']].corr().iloc[0,1], COMMON[COMMON.conf==1][['peer_adj_ret100','bench_adj_ret_pct']].corr().iloc[0,1], COMMON.assign(a=COMMON.peer_adj_ret100-COMMON.groupby('fy').peer_adj_ret100.transform('mean'), b=COMMON.bench_adj_ret_pct-COMMON.groupby('fy').bench_adj_ret_pct.transform('mean'))[['a','b']].corr().iloc[0,1]))
P("  conflicted CIOs, mean by half (common sample): peer-adj first %.3f second %.3f | bench-adj first %.3f second %.3f" % (CC[CC.second==0].peer_adj_ret100.mean(), CC[CC.second==1].peer_adj_ret100.mean(), CC[CC.second==0].bench_adj_ret_pct.mean(), CC[CC.second==1].bench_adj_ret_pct.mean()))
P("  plan's own benchmark return minus peer average, conflicted CIOs: first half %.3f, second half %.3f  (bench-adj = peer-adj + (peer avg - own benchmark))" % ((CC[CC.second==0].peer_adj_ret100-CC[CC.second==0].bench_adj_ret_pct).mean()*-1, (CC[CC.second==1].peer_adj_ret100-CC[CC.second==1].bench_adj_ret_pct).mean()*-1))
open('/home/user/PensionData/referee_response/time_to_departure/results_common_sample.md','w').write('\n'.join(out))
