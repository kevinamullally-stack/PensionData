import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf, json
from scipy import stats
df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_do.pkl')).sort_values(['ppd_id','fy']).copy()
df['fye_id'] = df.fye1.astype(str); df['fye_m'] = df.fye1.dt.month
df['bench_ret_pct'] = df.fund_benchmark*100
TW = {'EQTotal_Trgt':'t_eq','FITotal_Trgt':'t_fi','RETotal_Trgt':'t_re','PETotal_Trgt':'t_pe','HFTotal_Trgt':'t_hf','AltMiscTotal_Trgt':'t_alt','COMDTotal_Trgt':'t_comd','CashTotal_Trgt':'t_cash'}
for k,v in TW.items(): df[v] = df[k]*100
TGT = ['t_eq','t_fi','t_re','t_pe','t_hf','t_alt','t_comd']     # cash omitted (weights sum to 100)
# asset-class benchmark returns from the collected file
b = pd.read_csv((__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'benchmarks_collected.csv'), low_memory=False)
R = {'us_equity_benchmark_return_pct':'bx_us','intl_equity_benchmark_return_pct':'bx_intl','fixed_income_benchmark_return_pct':'bx_fi','real_estate_benchmark_return_pct':'bx_re','private_equity_benchmark_return_pct':'bx_pe','hedge_fund_absolute_return_benchmark_return_pct':'bx_hf','total_fund_benchmark_return_pct':'bx_tot'}
df = df.merge(b[['ppd_id','fy']+list(R)].rename(columns=R), on=['ppd_id','fy'], how='left')
S = df[(df.cio_dum==1)&(df.fy<=2020)&(df.curr1==0)].copy()
S['young']=np.where(S.cio_age<=46,1.0,np.where(S.cio_age>46,0.0,np.nan)); S['highrate']=np.where(S.InvestmentReturnAssumption_GASB>0.08,1.0,np.where(S.InvestmentReturnAssumption_GASB<=0.08,0.0,np.nan)); S['highfund']=np.where(S.ActFundedRatio_GASB100>=92,1.0,np.where(S.ActFundedRatio_GASB100<92,0.0,np.nan))
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
def psd(m):
    V=np.asarray(m._vcov); e,Q=np.linalg.eigh((V+V.T)/2); return (Q*np.clip(e,0,None))@Q.T
def lc(m,w):
    V=psd(m); names=list(m._coefnames); bb=np.asarray(m._beta_hat); c=np.zeros(len(names))
    for k,v in w.items():
        if k not in names: return dict(est=np.nan,se=np.nan,t=np.nan,p=np.nan)
        c[names.index(k)]=v
    est=float(c@bb); se=float(np.sqrt(max(c@V@c,0))); t=est/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),min(m._G)-1) if se>0 else np.nan; return dict(est=est,se=se,t=t,p=p)
def fit(y,rhs,fe,d): return pf.feols(f'{y} ~ {" + ".join(rhs)} | {fe}', data=d, vcov={'CRV1':'ppd_id + fy'})
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fmt(r): return "    n/a" if np.isnan(r['est']) else f"{r['est']:7.3f}{star(r['p']):3s}({r['t']:5.2f})"
RES = {}
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("# Benchmark returns: conflicted vs unconflicted CIOs, and across cross-sectional groups")
P(f"Sample: Table III sample (cio_dum==1, fy<=2020, curr1==0) with a hand-collected policy benchmark: {S.bench_ret_pct.notna().sum()} plan-years, {S[S.bench_ret_pct.notna()].ppd_id.nunique()} plans, {int(S[S.bench_ret_pct.notna()].conf_pen_vendor.sum())} conflicted plan-years.")
P("Dependent variable: plan's total-fund policy benchmark return (pp). All regressions absorb fiscal-year-end date (fye1) effects, so comparisons are within plans sharing the same 12-month window. SE double clustered by plan and fiscal year; t in parentheses.")
# ---------------- Table B1: conflicted vs unconflicted
COLS = [('(1)', [], 'fye_id', 'No','No'), ('(2)', TGT, 'fye_id', 'Yes','No'), ('(3)', TGT+C1+C3+C4+C5, 'fye_id', 'Yes','No'), ('(4)', TGT+C1+C3+C4+C5, 'ppd_id + fye_id', 'Yes','Yes')]
P("\n## Table B1. Policy benchmark return, Conflicted vs unconflicted")
P("col | controls | plan FE | Conflicted coef (t) | N | adj R2")
RES['B1']=[]
for name,ctrl,fe,tw,pfe in COLS:
    m=fit('bench_ret_pct',['conf_pen_vendor']+ctrl,fe,S); r=lc(m,{'conf_pen_vendor':1})
    RES['B1'].append(dict(col=name,tw=tw,pfe=pfe,ctrl=ctrl,fe=fe,conf=r,N=int(m._N),adjr2=float(m._adj_r2),est={n:(float(m.coef()[n]),float(np.sqrt(psd(m)[i,i]))) for i,n in enumerate(m._coefnames)}))
    P(f"{name} | target wts: {tw}, Table III ctrls: {'Yes' if C1[0] in ctrl else 'No'} | plan FE {pfe} | {fmt(r)} | {m._N} | {m._adj_r2:.3f}")
# also: peer-adjusted benchmark return (benchmark minus leave-one-out mean within fye1) as a descriptive check
g=S.groupby('fye_id').bench_ret_pct; S['bench_peeradj'] = S.bench_ret_pct - (g.transform('sum')-S.bench_ret_pct)/(g.transform('count')-1)
P(f"Descriptive: mean benchmark return minus same-fye1 peer average: conflicted {S[S.conf_pen_vendor==1].bench_peeradj.mean():.3f}, unconflicted {S[S.conf_pen_vendor==0].bench_peeradj.mean():.3f} (pp)")
# ---------------- Table B2: cross-sectional splits (paper format), y = benchmark return, do-file controls (+ target weights)
SPLITS=[('Underpaid','underpaid',C1+C3+['l_log_cio_tenure','l_log_cio_age','l_sib1','wstate_political'],('Underpaid','Not Underpaid')),
 ('Young','young',C1+C3+['l_sib1','wstate_political'],('Young','Not Young')),
 ('High funding','highfund',['l_invret','size']+C3+['l_log_cio_tenure'],('High Funding','Lower Funding')),
 ('Financial center','fincenter1',C1+['l_log_cio_tenure','l_sib1','wstate_political'],('Financial Center','Non-Financial Center')),
 ('Prior private experience','prior_private_exp',C1+C3+['l_log_cio_tenure','l_sib1','wstate_political'],('Prior Private Exp.','No Prior Private Exp.')),
 ('High discount rate','highrate',C1+C3+['l_log_cio_tenure','l_sib1','wstate_political'],('High Discount Rate','Not High Discount Rate'))]
RES['B2']={}
for spec,specl in [('A','without target-weight controls'),('B','with target-weight controls')]:
    P(f"\n## Table B2{spec}. Policy benchmark return by cross-sectional group ({specl}; do-file controls interacted with the split; fye1 FE)")
    P(f"{'split':26s} {'group x Conflicted':24s} {'other group x Conflicted':24s} {'p(equal)':8s} N")
    RES['B2'][spec]=[]
    for name,sv,ctrls,(l1,l0) in SPLITS:
        d=S.dropna(subset=[sv]).copy(); d['g1']=d[sv].astype(float); d['g0']=1-d.g1; d['g1_conf']=d.g1*d.conf_pen_vendor; d['g0_conf']=d.g0*d.conf_pen_vendor; rhs=['g1_conf','g0_conf','g1']
        cs = ctrls+(TGT if spec=='B' else C2)
        for c in cs: d[f'g1_{c}']=d.g1*d[c]; d[f'g0_{c}']=d.g0*d[c]; rhs+=[f'g1_{c}',f'g0_{c}']
        m=fit('bench_ret_pct',rhs,'fye_id',d); a=lc(m,{'g1_conf':1}); b0=lc(m,{'g0_conf':1}); de=lc(m,{'g1_conf':1,'g0_conf':-1})
        RES['B2'][spec].append(dict(name=name,l1=l1,l0=l0,a=a,b=b0,d=de,N=int(m._N),adjr2=float(m._adj_r2)))
        P(f"{name:26s} {fmt(a):24s} {fmt(b0):24s} {de['p']:<8.3f} {m._N}")
# ---------------- Table B3: among conflicted CIOs only
P("\n## Table B3. Among conflicted CIOs only: policy benchmark return on the group indicator (fye1 FE)")
P(f"{'group indicator':26s} {'(1) no controls':26s} {'(2) + target weights':26s} {'(3) + Table III controls':26s}")
CONF = S[S.conf_pen_vendor==1].copy(); RES['B3']=[]
for name,sv,ctrls,(l1,l0) in SPLITS:
    row=dict(name=name,l1=l1,cols=[])
    for ctrl in [[],TGT,TGT+C1+C3+C4+C5]:
        d=CONF.dropna(subset=[sv]).copy(); d['grp']=d[sv].astype(float)
        try:
            m=fit('bench_ret_pct',['grp']+[c for c in ctrl if c!=sv],'fye_id',d); r=lc(m,{'grp':1}); row['cols'].append(dict(r=r,N=int(m._N),adjr2=float(m._adj_r2)))
        except Exception as ex: row['cols'].append(dict(r=dict(est=np.nan,se=np.nan,t=np.nan,p=np.nan),N=0,adjr2=np.nan))
    RES['B3'].append(row)
    P(f"{l1+' (0/1)':26s} " + " ".join(f"{fmt(c['r']):18s} N={c['N']:<5d}" for c in row['cols']))
# ---------------- Table B4: asset-class benchmark returns, conflicted vs unconflicted and by split (fye1 FE)
P("\n## Table B4. Asset-class benchmark (index) returns, conflicted vs unconflicted (fye1 FE; (1) no controls, (2) target weights + Table III controls)")
CLS=[('bx_us','U.S. equity'),('bx_intl','Intl equity'),('bx_fi','Fixed income'),('bx_re','Real estate'),('bx_pe','Private equity'),('bx_hf','Hedge funds'),('bx_tot','Total fund (collected file)')]
RES['B4']=[]
for v,lab in CLS:
    d=S.dropna(subset=[v]); row=dict(lab=lab,cols=[])
    for ctrl in [[],TGT+C1+C3+C4+C5]:
        m=fit(v,['conf_pen_vendor']+ctrl,'fye_id',d); r=lc(m,{'conf_pen_vendor':1}); row['cols'].append(dict(r=r,N=int(m._N),adjr2=float(m._adj_r2)))
    RES['B4'].append(row); P(f"  {lab:28s} " + " | ".join(f"{fmt(c['r'])} N={c['N']}" for c in row['cols']) + f"   (sd within fye1: {(d[v]-d.groupby('fye_id')[v].transform('mean')).std():.2f})")
P("\n## Table B5. Asset-class benchmark returns by cross-sectional group (fye1 FE; target weights + do-file controls interacted): group x Conf | other x Conf | p(equal)")
RES['B5']={}
for name,sv,ctrls,(l1,l0) in SPLITS[:5]:
    P(f"  {name}:"); RES['B5'][name]=[]
    for v,lab in CLS[:6]:
        d=S.dropna(subset=[sv,v]).copy(); d['g1']=d[sv].astype(float); d['g0']=1-d.g1; d['g1_conf']=d.g1*d.conf_pen_vendor; d['g0_conf']=d.g0*d.conf_pen_vendor; rhs=['g1_conf','g0_conf','g1']
        for c in ctrls+TGT: d[f'g1_{c}']=d.g1*d[c]; d[f'g0_{c}']=d.g0*d[c]; rhs+=[f'g1_{c}',f'g0_{c}']
        try:
            m=fit(v,rhs,'fye_id',d); a=lc(m,{'g1_conf':1}); b0=lc(m,{'g0_conf':1}); de=lc(m,{'g1_conf':1,'g0_conf':-1}); N=int(m._N)
        except Exception: a=b0=de=dict(est=np.nan,se=np.nan,t=np.nan,p=np.nan); N=0
        RES['B5'][name].append(dict(lab=lab,l1=l1,l0=l0,a=a,b=b0,d=de,N=N))
        P(f"    {lab:16s} {fmt(a):24s} {fmt(b0):24s} {'' if np.isnan(de['p']) else f'{de['p']:.3f}':8s} N={N}")
open('/home/user/PensionData/referee_response/time_to_departure/results_benchmark_returns.md','w').write('\n'.join(out))
pd.to_pickle(RES,'bench_compare_res.pkl'); S.to_pickle('bench_compare_S.pkl')
