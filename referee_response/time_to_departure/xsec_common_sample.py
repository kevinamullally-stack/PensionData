import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_do.pkl')).sort_values(['ppd_id','fy']).copy()
S = df[(df.cio_dum==1)&(df.fy<=2020)&(df.curr1==0)].copy()
S['gap'] = S.bench_adj_ret_pct - S.peer_adj_ret100          # = peer average return - plan's own benchmark return (pp)
COM = S[S.peer_adj_ret100.notna() & S.bench_adj_ret_pct.notna()].copy()
S['young']=np.where(S.cio_age<=46,1.0,np.where(S.cio_age>46,0.0,np.nan)); COM['young']=np.where(COM.cio_age<=46,1.0,np.where(COM.cio_age>46,0.0,np.nan))
for d in (S,COM):
    d['highrate']=np.where(d.InvestmentReturnAssumption_GASB>0.08,1.0,np.where(d.InvestmentReturnAssumption_GASB<=0.08,0.0,np.nan))
    d['highfund']=np.where(d.ActFundedRatio_GASB100>=92,1.0,np.where(d.ActFundedRatio_GASB100<92,0.0,np.nan))
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']
SPLITS=[('Underpaid','underpaid',C1+C2+C3+['l_log_cio_tenure','l_log_cio_age','l_sib1','wstate_political'],('Underpaid','Not underpaid')),
 ('Young','young',C1+C2+C3+['l_sib1','wstate_political'],('Young','Not young')),
 ('High discount rate','highrate',C1+C2+C3+['l_log_cio_tenure','l_sib1','wstate_political'],('High rate','Low rate')),
 ('High funding','highfund',['l_invret','size']+C2+C3+['l_log_cio_tenure'],('High funding','Low funding')),
 ('Financial center','fincenter1',C1+C2+['l_log_cio_tenure','l_sib1','wstate_political'],('Fin. center','Not fin. center')),
 ('Prior private experience','prior_private_exp',C1+C2+C3+['l_log_cio_tenure','l_sib1','wstate_political'],('Prior private','No prior private'))]
def psd_lc(m,w):
    V=np.asarray(m._vcov); e,Q=np.linalg.eigh((V+V.T)/2); V=(Q*np.clip(e,0,None))@Q.T; names=list(m._coefnames); b=np.asarray(m._beta_hat); c=np.zeros(len(names))
    for k,v in w.items(): c[names.index(k)]=v
    est=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=est/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),min(m._G)-1) if se>0 else np.nan; return est,t,p
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f(e,t,p): return f"{e:7.3f}{star(p):3s}({t:5.2f})"
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P(f"Common sample (peer-adj and bench-adj both non-missing): {len(COM)} plan-years, {COM.ppd_id.nunique()} plans, conflicted share {COM.conf_pen_vendor.mean():.3f} | full Table III sample: {len(S)} plan-years, {S.ppd_id.nunique()} plans, conflicted share {S.conf_pen_vendor.mean():.3f}")
P("Dependent variables: Peer-adj; Bench-adj; Gap = Bench-adj minus Peer-adj = (peer average return - plan's own benchmark return). Year FE, controls interacted with the split as in the do-file, SE double clustered by plan & year.\n")
P("## Table III baseline (col 1 spec: base controls, year FE), common sample")
for y,yl in [('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj'),('gap','Gap')]:
    m=pf.feols(f'{y} ~ conf_pen_vendor + {" + ".join(C1+C2+C3)} | fy', data=COM, vcov={'CRV1':'ppd_id + fy'}); P(f"  {yl:10s} Conflicted {f(*psd_lc(m,{'conf_pen_vendor':1}))} N={m._N}")
for name,sv,ctrls,(l1,l0) in SPLITS:
    P(f"\n## {name} (split on {sv})")
    P(f"{'sample / dependent variable':44s} {l1+' x Conf':24s} {l0+' x Conf':24s} {'p(equal)':9s} N")
    for samp,sl in [(S,'Full sample'),(COM,'Common sample')]:
        d=samp.dropna(subset=[sv]).copy(); d['g1']=d[sv].astype(float); d['g0']=1-d.g1; d['g1_conf']=d.g1*d.conf_pen_vendor; d['g0_conf']=d.g0*d.conf_pen_vendor
        rhs=['g1_conf','g0_conf','g1']
        for c in ctrls: d[f'g1_{c}']=d.g1*d[c]; d[f'g0_{c}']=d.g0*d[c]; rhs+=[f'g1_{c}',f'g0_{c}']
        ys=[('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj'),('gap','Gap (bench - peer)')] if samp is COM else [('peer_adj_ret100','Peer-adj'),('bench_adj_ret_pct','Bench-adj')]
        for y,yl in ys:
            m=pf.feols(f'{y} ~ {" + ".join(rhs)} | fy', data=d, vcov={'CRV1':'ppd_id + fy'})
            a=psd_lc(m,{'g1_conf':1}); b=psd_lc(m,{'g0_conf':1}); dd=psd_lc(m,{'g1_conf':1,'g0_conf':-1})
            P(f"{sl+' / '+yl:44s} {f(*a):24s} {f(*b):24s} {dd[2]:<9.3f} {m._N}")
# raw group means of the gap for conflicted vs not, by split, common sample
P("\n## Raw means of Gap (peer avg - own benchmark, pp) in the common sample: conflicted vs non-conflicted, by subgroup")
for name,sv,_,(l1,l0) in SPLITS:
    g=COM.dropna(subset=[sv]).groupby([sv,'conf_pen_vendor']).gap.mean().unstack()
    P(f"  {name:26s} {l1:16s}: conf {g.loc[1.0,1]:6.2f} non-conf {g.loc[1.0,0]:6.2f} | {l0:16s}: conf {g.loc[0.0,1]:6.2f} non-conf {g.loc[0.0,0]:6.2f}")
open('/home/user/PensionData/referee_response/time_to_departure/results_xsec_common_sample.md','w').write('\n'.join(out))
