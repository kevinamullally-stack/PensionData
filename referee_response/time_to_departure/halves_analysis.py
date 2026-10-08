"""Sharpened first-half vs second-half tenure tests. Run after ttd_analysis.py (needs df_built.pkl next to this script)."""
import os
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
pd.set_option('display.width', 220)
df = pd.read_pickle(os.path.join(os.path.dirname(os.path.abspath(__file__)),'df_built.pkl')).sort_values(['spell','fy']).copy()
CTRL = 'size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB + sib1 + cio_age + cio_tenure + prior_private_exp + Elite_inst'
CS = 'size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB'
# ---- tenure at departure, halves, fraction elapsed (departing spells only)
dep = df.departs_obs==1
g = df[dep].groupby('spell')
df['ten_dep'] = np.nan
df.loc[dep,'ten_dep'] = (g.cio_tenure.transform('max') + (g.year_departs.transform('max') - g.fy.transform('max')).clip(lower=0))
df['second'] = np.where(dep & df.ten_dep.notna() & (df.ten_dep>0), (df.cio_tenure > df.ten_dep/2).astype(float), np.nan)
df['frac'] = np.where(dep & (df.ten_dep>0), df.cio_tenure/df.ten_dep, np.nan)
df['last2'] = np.where(dep, (df.ttd>=-1).astype(float), np.nan)
df['other_dep'] = (df.dep_type=='other').astype(int)
for v in ['second','frac','last2']:
    df[f'c_{v}'] = df.conf_cio*df[v]; df[f'o_{v}'] = df.other_dep*df[v]
S = df[df.second.notna() & df.dep_type.isin(['conf','other'])].copy()
def star(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def lc(m, w):
    names=list(m._coefnames); b=np.asarray(m._beta_hat); V=np.asarray(m._vcov); c=np.zeros(len(names))
    for k,v in w.items():
        if k not in names: return (np.nan,np.nan,np.nan,np.nan)
        c[names.index(k)]=v
    e=c@b; se=np.sqrt(c@V@c); G=m._G[0]; p=2*stats.t.sf(abs(e/se),G-1); return e,se,p,stats.t.ppf(.975,G-1)
def f3(e,se,p,*a): return f"{e:6.2f}{star(p):3s}({se:.2f})"
print("counts: conflicted CIO-years first/second half:", S[S.conf_cio==1].second.value_counts().sort_index().tolist(), "| distinct conflicted CIOs:", S[S.conf_cio==1].cio.nunique(), "| other departers CIOs:", S[S.other_dep==1].cio.nunique())
print("\n=== 1. Halves with tenure at departure; clustering by plan / CIO / system ===")
print(f"{'outcome':8s} {'FE':12s} {'cluster':8s} | {'conf 2nd-1st':18s} {'other 2nd-1st':18s} {'difference':18s} 95% CI diff")
for y in ['ret100','bret100']:
    for fe,ctrl in [('ppd_id + fy',CTRL),('spell + fy',CS)]:
        for cl in ['ppd_id','cio','system_id']:
            rhs = (f'conf_cio + ' if fe.startswith('ppd') else '') + f'c_second + o_second + {ctrl}'
            m = pf.feols(f'{y} ~ {rhs} | {fe}', data=S, vcov={'CRV1':cl})
            a=lc(m,{'c_second':1}); b=lc(m,{'o_second':1}); d=lc(m,{'c_second':1,'o_second':-1})
            print(f"{y:8s} {fe:12s} {cl:8s} | {f3(*a):18s} {f3(*b):18s} {f3(*d):18s} [{d[0]-d[3]*d[1]:.2f}, {d[0]+d[3]*d[1]:.2f}]  N={m._N}")
print("\n=== 2. Person-level paired test: each CIO's mean return in 2nd half minus 1st half (plans averaged within CIO-year) ===")
P = S.groupby(['cio','conf_cio','fy','second'], as_index=False)[['ret100','bret100']].mean()
for y in ['ret100','bret100']:
    H = P.groupby(['cio','conf_cio','second'])[y].mean().unstack('second').dropna()
    H['chg'] = H[1.0]-H[0.0]
    for grp,lab in [(1,'conflicted'),(0,'other departers')]:
        x = H.xs(grp, level='conf_cio').chg
        t,p = stats.ttest_1samp(x,0); w = stats.wilcoxon(x).pvalue if len(x)>10 else np.nan; sgn = stats.binomtest(int((x>0).sum()), len(x)).pvalue
        print(f"{y:8s} {lab:16s}: n={len(x):3d} mean change {x.mean():6.2f} median {x.median():6.2f} share improving {(x>0).mean():.2f} | paired t p={p:.3f}  Wilcoxon p={w:.3f}  sign p={sgn:.3f}")
    xc = H.xs(1,level='conf_cio').chg; xo = H.xs(0,level='conf_cio').chg
    print(f"{y:8s} conflicted minus other change: {xc.mean()-xo.mean():6.2f}  Welch p={stats.ttest_ind(xc,xo,equal_var=False).pvalue:.3f}  Mann-Whitney p={stats.mannwhitneyu(xc,xo).pvalue:.3f}")
print("\n=== 3. Continuous: fraction of tenure elapsed (0=start, 1=departure); coefficient = change from start to end of tenure ===")
for y in ['ret100','bret100']:
    for fe,ctrl in [('ppd_id + fy',CTRL),('spell + fy',CS)]:
        rhs = (f'conf_cio + ' if fe.startswith('ppd') else '') + f'c_frac + o_frac + {ctrl}'
        m = pf.feols(f'{y} ~ {rhs} | {fe}', data=S, vcov={'CRV1':'cio'})
        a=lc(m,{'c_frac':1}); b=lc(m,{'o_frac':1}); d=lc(m,{'c_frac':1,'o_frac':-1})
        print(f"{y:8s} {fe:12s} | conf {f3(*a):18s} other {f3(*b):18s} diff {f3(*d):18s} N={m._N}")
print("\n=== 4. Cleaner contrasts ===")
S4 = S[S.ten_dep>=4]
for y in ['ret100','bret100']:
    m = pf.feols(f'{y} ~ c_second + o_second + {CS} | spell + fy', data=S4, vcov={'CRV1':'cio'})
    a=lc(m,{'c_second':1}); d=lc(m,{'c_second':1,'o_second':-1})
    print(f"{y:8s} tenure>=4 only, within CIO: conf 2nd-1st {f3(*a):18s} diff vs other {f3(*d):18s} N={m._N}  (conf CIOs {S4[S4.conf_cio==1].cio.nunique()})")
    m = pf.feols(f'{y} ~ c_last2 + o_last2 + {CS} | spell + fy', data=S, vcov={'CRV1':'cio'})
    a=lc(m,{'c_last2':1}); d=lc(m,{'c_last2':1,'o_last2':-1})
    print(f"{y:8s} last 2 yrs vs earlier, within CIO: conf {f3(*a):18s} diff vs other {f3(*d):18s} N={m._N}")
print("\n=== 5. Randomization inference: permute 'conflicted' across departing CIOs (person level), within-CIO halves DiD ===")
rng = np.random.default_rng(7)
def did(d):
    m = pf.feols(f'ret100 ~ c_second + o_second + {CS} | spell + fy', data=d, vcov='iid'); return m.coef()['c_second']-m.coef()['o_second']
obs = did(S); cios = S.cio.unique(); ncf = S[S.conf_cio==1].cio.nunique(); null=[]
for i in range(500):
    lab = pd.Series(0, index=cios); lab[rng.choice(cios, ncf, replace=False)] = 1
    d = S.copy(); d['conf_cio'] = d.cio.map(lab).values; d['other_dep'] = 1-d['conf_cio']; d['c_second']=d.conf_cio*d.second; d['o_second']=d.other_dep*d.second
    null.append(did(d))
null = np.array(null); print(f"observed DiD (peer-adj, within CIO) = {obs:.2f}; RI two-sided p = {(np.abs(null)>=abs(obs)).mean():.3f}; one-sided p(DiD <= obs, i.e. acceleration) = {(null<=obs).mean():.3f}; 500 permutations")
print("\n=== 6. Equivalence bounds: largest conflicted-specific second-half deterioration the 95% CI allows (within CIO, cluster by CIO) ===")
for y in ['ret100','bret100']:
    m = pf.feols(f'{y} ~ c_second + o_second + {CS} | spell + fy', data=S, vcov={'CRV1':'cio'})
    a=lc(m,{'c_second':1}); d=lc(m,{'c_second':1,'o_second':-1})
    print(f"{y:8s}: conf own change 95% CI [{a[0]-a[3]*a[1]:.2f}, {a[0]+a[3]*a[1]:.2f}] | DiD 95% CI [{d[0]-d[3]*d[1]:.2f}, {d[0]+d[3]*d[1]:.2f}]  -> can rule out a conflict-specific deterioration larger than {max(0,-(d[0]-d[3]*d[1])):.2f} pp")
print("\n=== 7. Stacked asset-class peer-adjusted returns (eq, fi, re, pe, hf), asset x year and plan x asset FE, cluster by CIO ===")
L = []
for a in ['eq','fi','re','pe','hf']:
    t = S[['ppd_id','fy','cio','spell','conf_cio','other_dep','second','c_second','o_second','size','ActFundedRatio_GASB','InvestmentReturnAssumption_GASB',f'peer_adj_{a}_ret']].rename(columns={f'peer_adj_{a}_ret':'y'}).dropna(subset=['y']); t['asset']=a; L.append(t)
L = pd.concat(L); L['y100']=L.y*100; L['ay']=L.asset+'_'+L.fy.astype(str); L['pa']=L.ppd_id.astype(str)+'_'+L.asset; L['sa']=L.spell.astype(str)+'_'+L.asset
m = pf.feols(f'y100 ~ conf_cio + c_second + o_second + {CS} | pa + ay', data=L, vcov={'CRV1':'cio'})
print(f"all classes pooled, plan x asset FE: conf level {f3(*lc(m,{'conf_cio':1}))} conf 2nd-1st {f3(*lc(m,{'c_second':1}))} diff vs other {f3(*lc(m,{'c_second':1,'o_second':-1}))} N={m._N}")
m = pf.feols(f'y100 ~ c_second + o_second + {CS} | sa + ay', data=L, vcov={'CRV1':'cio'})
print(f"all classes pooled, spell x asset FE:  conf 2nd-1st {f3(*lc(m,{'c_second':1}))} diff vs other {f3(*lc(m,{'c_second':1,'o_second':-1}))} N={m._N}")
for a in ['eq','fi','re','pe','hf']:
    d = L[L.asset==a]; m = pf.feols(f'y100 ~ conf_cio + c_second + o_second + {CS} | ppd_id + fy', data=d, vcov={'CRV1':'cio'})
    print(f"  {a:3s}: conf level {f3(*lc(m,{'conf_cio':1}))} conf 2nd-1st {f3(*lc(m,{'c_second':1}))} diff vs other {f3(*lc(m,{'c_second':1,'o_second':-1}))} N={m._N}")
