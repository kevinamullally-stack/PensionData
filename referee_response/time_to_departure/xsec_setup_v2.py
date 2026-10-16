import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
S = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'table3_newbench_S_v2.pkl')).copy()
S['py'] = S.ppd_id.astype(int)*10000 + S.fy.astype(int); S['fye_id'] = S.fye1.astype(str)
S['pf'] = S.ppd_id.astype(str)+'_'+S.fye_id
# split indicators with Stata's missing-value semantics, exactly as the do-file creates them
S['young'] = np.where(S.cio_age.isna(), np.nan, np.where(S.cio_age<=46, 1.0, 0.0))   # missing age -> missing
ira = S.InvestmentReturnAssumption_GASB
S['highrate'] = np.where(ira.isna(), np.nan, np.where(ira>0.08, 1.0, 0.0))
fr = S.ActFundedRatio_GASB100
S['highfund'] = np.where(fr.isna(), np.nan, np.where(fr>=92, 1.0, 0.0))            # missing funding -> missing; defined from the funding ratio only
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']
SPLITS = [  # key, split var, interacted controls (do-file control globals at that block), cluster pair, labels, paper table/panel
 ('underpaid','underpaid', C1+C2+C3+['l_log_cio_tenure','l_log_cio_age','l_sib1','wstate_political'], ('ppd_id','fy'), ('Underpaid CIOs','Not Underpaid CIOs'), 'Table V, Panel A'),
 ('young','young',         C1+C2+C3+['l_sib1','wstate_political'],                                     ('ppd_id','fy'), ('Young CIOs','Not Young CIOs'), 'Table V, Panel B'),
 ('priv','prior_private_exp', C1+C2+C3+['l_log_cio_tenure','l_sib1','wstate_political'],               ('ppd_id','fy'), ('Prior Private Exp.','No Prior Private Exp.'), 'Table VI, Panel A'),
 ('fin','fincenter1',      C1+C2+['l_log_cio_tenure','l_sib1','wstate_political'],                     ('ppd_id','fye_id'), ('Financial Center','Non-Financial Center'), 'Table VI, Panel B'),
 ('rate','highrate',       C1+C2+C3+['l_log_cio_tenure','l_sib1','wstate_political'],                  ('ppd_id','fy'), ('High Discount Rate','Not High Discount Rate'), 'Table VII, Panel A'),
 ('fund','highfund',       ['l_invret','size']+C2+C3+['l_log_cio_tenure'],                             ('ppd_id','fy'), ('High Funding','Lower Funding'), 'Table VII, Panel B'),
]
RAW = pf.ssc(adj=False, fixef_k='none', cluster_adj=False)
def build(sv, ctrls):
    d = S.dropna(subset=[sv]).copy(); d['g1']=d[sv].astype(float); d['g0']=1-d.g1
    d['g1_conf']=d.g1*d.conf_pen_vendor; d['g0_conf']=d.g0*d.conf_pen_vendor; rhs=['g1_conf','g0_conf','g1']
    for c in ctrls:
        if c==sv: continue                         # fin x fincenter1 is collinear with the main effect; Stata omits it
        d[f'g1_{c}']=d.g1*d[c]; d[f'g0_{c}']=d.g0*d[c]; rhs+=[f'g1_{c}',f'g0_{c}']
    return d, rhs
def est(y, sv, ctrls, cl, psd=True):
    d, rhs = build(sv, ctrls)
    inter = d[cl[0]].astype(str)+'#'+d[cl[1]].astype(str); d['_int']=inter
    f = f'{y} ~ {" + ".join(rhs)} | fy'
    fits = {c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in [cl[0], cl[1], '_int']}
    m = fits[cl[0]]; V = np.asarray(fits[cl[0]]._vcov)+np.asarray(fits[cl[1]]._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits[cl[0]]._G[0]), int(fits[cl[1]]._G[0])); K=len(names)+1
    V *= (N-1)/(N-K)*G/(G-1)
    if psd:
        w,Q=np.linalg.eigh((V+V.T)/2)
        if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat)
    def lc(wd):
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),G-1) if se>0 else np.nan
        return dict(est=e,se=se,t=t,p=p)
    madj = pf.feols(f, data=d, vcov='iid')
    return dict(a=lc({'g1_conf':1}), b=lc({'g0_conf':1}), d=lc({'g1_conf':1,'g0_conf':-1}), N=int(N), G=G, adjr2=float(madj._adj_r2))
