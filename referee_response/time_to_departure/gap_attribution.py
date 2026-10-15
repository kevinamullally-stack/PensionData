import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
pd.set_option('display.width',230)
df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_do.pkl')).sort_values(['ppd_id','fy']).copy()
b = pd.read_csv((__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'benchmarks_collected.csv'), low_memory=False)
R = {'us':'us_equity_benchmark_return_pct','intl':'intl_equity_benchmark_return_pct','glob':'global_equity_benchmark_return_pct','fi':'fixed_income_benchmark_return_pct','re':'real_estate_benchmark_return_pct',
     'pe':'private_equity_benchmark_return_pct','hf':'hedge_fund_absolute_return_benchmark_return_pct','comd':'real_assets_commodities_benchmark_return_pct','cash':'cash_benchmark_return_pct','tot':'total_fund_benchmark_return_pct'}
bb = b[['ppd_id','fy']+list(R.values())].rename(columns={v:f'ix_{k}' for k,v in R.items()})
# plan-level equity index: 60/40 US/intl when both, else whichever exists, else global
bb['ix_eq'] = np.where(bb.ix_us.notna()&bb.ix_intl.notna(), 0.6*bb.ix_us+0.4*bb.ix_intl, bb.ix_us.fillna(bb.ix_intl).fillna(bb.ix_glob))
d = df.merge(bb, on=['ppd_id','fy'], how='left')
d['fye_m'] = d.fye1.dt.month
d = d[d.fye_m==6].copy()   # June fiscal-year-end plans only: homogeneous market timing within a fiscal year
d['B'] = d.fund_benchmark*100          # authors' hand-collected total-fund benchmark return (pp)
ok = d.dropna(subset=['B','ix_tot'])
print(f"agreement of the file's total-fund benchmark return with the dataset's fund_benchmark: n={len(ok)}, corr {ok.B.corr(ok.ix_tot):.3f}, within 0.1pp {((ok.B-ok.ix_tot).abs()<0.1).mean():.1%}, within 1pp {((ok.B-ok.ix_tot).abs()<1).mean():.1%}")
# --- class weights (target, decimals) and class index returns
W = {'eq':'EQTotal_Trgt','fi':'FITotal_Trgt','re':'RETotal_Trgt','pe':'PETotal_Trgt','hf':'HFTotal_Trgt','comd':'COMDTotal_Trgt','cash':'CashTotal_Trgt','alt':'AltMiscTotal_Trgt'}
K = ['eq','fi','re','pe','hf','comd','cash']
# class-year average index return: within fy x FYE-month when >=5 plans, else fy
for k in K:
    d['cell'] = d.fy.astype(str)+'_'+d.fye_m.astype(str)
    d[f'ixbar_{k}'] = d.groupby('cell')[f'ix_{k}'].transform(lambda x: x.mean() if x.notna().sum()>=5 else np.nan)
    d[f'wbar_{k}'] = d.groupby('cell')[W[k]].transform('mean')
# components (pp). For a class with weight>0 but missing own index, use the class average (zero selection effect)
d['tsum']=d[[W[k] for k in W]].sum(axis=1, min_count=1)*100
d['tw_ok']=d.tsum.between(90,110)
d['B_syn']=0.0; d['alloc']=0.0; d['select']=0.0; d['inter']=0.0; d['n_own']=0; d['bar_ok']=True
for k in K:
    w = d[W[k]].fillna(0); wb = d[f'wbar_{k}'].fillna(0); r = d[f'ix_{k}']; rb = d[f'ixbar_{k}']
    d['bar_ok'] &= ~((w>0)&rb.isna())
    r_use = r.fillna(rb)
    has = rb.notna()                      # class usable only when a class-year average exists; otherwise it contributes nothing (plans with w>0 there are already excluded by bar_ok)
    d['B_syn'] += np.where(has, w*r_use, 0.0)
    d['alloc']  += np.where(has, (w-wb)*rb, 0.0)
    d['select'] += np.where(has, wb*(r_use-rb), 0.0)
    d['inter']  += np.where(has, (w-wb)*(r_use-rb), 0.0)
    d['n_own']  += r.notna().astype(int)
d['B_syn_bar'] = d.groupby('cell').B_syn.transform('mean')
chk = d.dropna(subset=['B','B_syn'])[d.n_own>=2]
print(f"synthetic policy benchmark (sum of target weights x own class index returns) vs authors' benchmark: n={len(chk)}, corr {chk.B.corr(chk.B_syn):.3f}; within-year corr {chk.assign(a=chk.B-chk.groupby('cell').B.transform('mean'), s=chk.B_syn-chk.groupby('cell').B_syn.transform('mean'))[['a','s']].corr().iloc[0,1]:.3f}; sd B {chk.B.std():.2f}, sd (B - B_syn) {(chk.B-chk.B_syn).std():.2f}")
# --- sample: Table III common sample with at least 2 own class indexes
S = d[(d.cio_dum==1)&(d.fy<=2020)&(d.curr1==0)].copy()
S['gap'] = S.bench_adj_ret_pct - S.peer_adj_ret100
S['gap_alloc'] = -S.alloc; S['gap_select'] = -S.select; S['gap_inter'] = -S.inter; S['gap_resid'] = S.gap - (-(S.B_syn - S.B_syn_bar))  # residual = part of (peer avg - B) not explained by the synthetic benchmark (year const absorbed)
COM = S[S.peer_adj_ret100.notna()&S.bench_adj_ret_pct.notna()&(S.n_own>=2)&S.tw_ok&S.bar_ok&S.B_syn.notna()].copy()
COM['young']=np.where(COM.cio_age<=46,1.0,np.where(COM.cio_age>46,0.0,np.nan)); COM['highrate']=np.where(COM.InvestmentReturnAssumption_GASB>0.08,1.0,np.where(COM.InvestmentReturnAssumption_GASB<=0.08,0.0,np.nan)); COM['highfund']=np.where(COM.ActFundedRatio_GASB100>=92,1.0,np.where(COM.ActFundedRatio_GASB100<92,0.0,np.nan))
print(f"\n[June FYE plans only] analysis sample: {len(COM)} plan-years, {COM.ppd_id.nunique()} plans, conflicted {int(COM.conf_pen_vendor.sum())} | own class indexes per plan-year: mean {COM.n_own.mean():.1f}")
chk2 = COM.assign(tot=COM.gap_alloc+COM.gap_select+COM.gap_inter+COM.gap_resid); print("adding-up check: within-year corr(gap, sum of components) = %.4f" % chk2.assign(a=chk2.gap-chk2.groupby("cell").gap.transform("mean"), b=chk2.tot-chk2.groupby("cell").tot.transform("mean"))[["a","b"]].corr().iloc[0,1])
print("sd of components (pp): gap %.2f | alloc %.2f | select %.2f | inter %.2f | resid %.2f" % tuple(COM[c].std() for c in ['gap','gap_alloc','gap_select','gap_inter','gap_resid']))
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']
SPLITS=[('Underpaid','underpaid',C1+C2+C3+['l_log_cio_tenure','l_log_cio_age','l_sib1','wstate_political'],('Underpaid','Not underpaid')),
 ('Young','young',C1+C2+C3+['l_sib1','wstate_political'],('Young','Not young')),
 ('High funding','highfund',['l_invret','size']+C2+C3+['l_log_cio_tenure'],('High funding','Low funding')),
 ('Financial center','fincenter1',C1+C2+['l_log_cio_tenure','l_sib1','wstate_political'],('Fin. center','Not fin. center')),
 ('Prior private experience','prior_private_exp',C1+C2+C3+['l_log_cio_tenure','l_sib1','wstate_political'],('Prior private','No prior private')),
 ('High discount rate','highrate',C1+C2+C3+['l_log_cio_tenure','l_sib1','wstate_political'],('High rate','Low rate'))]
def psd_lc(m,w):
    V=np.asarray(m._vcov); e,Q=np.linalg.eigh((V+V.T)/2); V=(Q*np.clip(e,0,None))@Q.T; names=list(m._coefnames); bb_=np.asarray(m._beta_hat); c=np.zeros(len(names))
    for k,v in w.items(): c[names.index(k)]=v
    est=float(c@bb_); se=float(np.sqrt(max(c@V@c,0))); t=est/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),min(m._G)-1) if se>0 else np.nan; return est,t,p
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f(e,t,p): return f"{e:7.3f}{star(p):3s}({t:5.2f})"
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("\n# Attribution of the benchmark gap (peer average return - own policy benchmark) by subgroup. Conflicted coefficients; fiscal-year x FYE-month FE; do-file controls interacted with the split; SE clustered plan & year.")
P("# gap = alloc + select + inter + resid.  alloc: own target weights vs peer-average weights at class-average index returns.  select: own class index returns vs class average, at peer-average weights (independent of the plan's allocation).  resid: part of the benchmark not reproduced by target weights x class indexes.")
YS=[('peer_adj_ret100','Peer-adjusted'),('bench_adj_ret_pct','Benchmark-adjusted'),('gap','Gap (total)'),('gap_alloc','  allocation effect'),('gap_select','  index-selection effect'),('gap_inter','  interaction'),('gap_resid','  residual')]
for name,sv,ctrls,(l1,l0) in SPLITS:
    dd=COM.dropna(subset=[sv]).copy(); dd['g1']=dd[sv].astype(float); dd['g0']=1-dd.g1; dd['g1_conf']=dd.g1*dd.conf_pen_vendor; dd['g0_conf']=dd.g0*dd.conf_pen_vendor
    rhs=['g1_conf','g0_conf','g1']
    for c in ctrls: dd[f'g1_{c}']=dd.g1*dd[c]; dd[f'g0_{c}']=dd.g0*dd[c]; rhs+=[f'g1_{c}',f'g0_{c}']
    P(f"\n## {name}:   {l1} x Conf | {l0} x Conf | p(equal)")
    for y,yl in YS:
        m=pf.feols(f'{y} ~ {" + ".join(rhs)} | cell', data=dd, vcov={'CRV1':'ppd_id + fy'})
        a=psd_lc(m,{'g1_conf':1}); b0=psd_lc(m,{'g0_conf':1}); de=psd_lc(m,{'g1_conf':1,'g0_conf':-1})
        P(f"  {yl:26s} {f(*a):22s} {f(*b0):22s} {de[2]:.3f}   N={m._N}")
# --- direct test of index selection by asset class: own index return minus class-year average, conflicted x subgroup
P("\n# Index selection by asset class: dependent variable = plan's own class benchmark return minus the class-year average (pp). Negative = softer index than peers. fiscal-year x FYE-month FE, base controls interacted; SE clustered plan & year.")
for k in ['eq','fi','re','pe','hf']:
    COM[f'rel_{k}'] = COM[f'ix_{k}'] - COM[f'ixbar_{k}']
P("Pooled (Table III col-1 style): conflicted coefficient on index-relative return:")
for k,kl in [('eq','Equity'),('fi','Fixed income'),('re','Real estate'),('pe','Private equity'),('hf','Hedge funds')]:
    dd=COM.dropna(subset=[f'rel_{k}'])
    m=pf.feols(f'rel_{k} ~ conf_pen_vendor + {" + ".join(C1+C2+C3)} | cell', data=dd, vcov={'CRV1':'ppd_id + fy'}); P(f"  {kl:15s} {f(*psd_lc(m,{'conf_pen_vendor':1}))} N={m._N}  (sd of dep var {dd[f'rel_{k}'].std():.2f})")
for name,sv,ctrls,(l1,l0) in SPLITS[:5]:
    P(f"\n## {name}: index-relative return, {l1} x Conf | {l0} x Conf | p(equal)")
    for k,kl in [('eq','Equity'),('fi','Fixed income'),('re','Real estate'),('pe','Private equity'),('hf','Hedge funds')]:
        dd=COM.dropna(subset=[sv,f'rel_{k}']).copy(); dd['g1']=dd[sv].astype(float); dd['g0']=1-dd.g1; dd['g1_conf']=dd.g1*dd.conf_pen_vendor; dd['g0_conf']=dd.g0*dd.conf_pen_vendor
        rhs=['g1_conf','g0_conf','g1']
        for c in C1+C2+C3: dd[f'g1_{c}']=dd.g1*dd[c]; dd[f'g0_{c}']=dd.g0*dd[c]; rhs+=[f'g1_{c}',f'g0_{c}']
        try:
            m=pf.feols(f'rel_{k} ~ {" + ".join(rhs)} | cell', data=dd, vcov={'CRV1':'ppd_id + fy'})
            a=psd_lc(m,{'g1_conf':1}); b0=psd_lc(m,{'g0_conf':1}); de=psd_lc(m,{'g1_conf':1,'g0_conf':-1})
            P(f"  {kl:15s} {f(*a):22s} {f(*b0):22s} {de[2]:.3f}   N={m._N}")
        except Exception as ex: P(f"  {kl:15s} ERROR {str(ex)[:50]}")
open('/home/user/PensionData/referee_response/time_to_departure/results_gap_attribution.md','w').write('\n'.join(out))
d.to_pickle('df_bench.pkl')
