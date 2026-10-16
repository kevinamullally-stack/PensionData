import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
d = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_newbench_v2.pkl')).sort_values(['ppd_id','fy']).copy()
d['py'] = d.ppd_id.astype(int)*10000 + d.fy.astype(int)
S = d[(d.cio_dum==1)&(d.fy<=2020)&(d.curr1==0)].copy()
for q in [5,10]:
    S[f'last{q}'] = S.conf_cio.astype(float)
    S.loc[S.year_departs.notna() & (S.conf_cio==1) & (S.fy <= S.year_departs - q), f'last{q}'] = 0.0
S['ret_gap'] = (S.invret100 - S.act_doc).abs()
Y = {
 'peer':     ('peer_adj_ret100', 'Peer-adjusted return (Panel A, unchanged)'),
 'b_orig':   ('bench_adj_ret_pct', 'Original benchmark-adjusted return (paper Panel B)'),
 'b_rep':    (None, 'PPD return minus updated reported benchmark'),
 'b_AB':     (None, 'PPD return minus updated benchmark (reported + inferred grade A/B)'),
 'b_AB_ok':  (None, 'PPD return minus updated benchmark (A/B), rows where PPD and document returns agree within 0.5 pp'),
 'b_docAB':  (None, 'Document return minus updated benchmark (reported + inferred grade A/B)'),
}
S['b_rep'] = S.invret100 - S.bm_rep
S['b_AB'] = S.invret100 - S.bm_AB
S['b_all'] = S.invret100 - S.bm_all
S['b_AB_ok'] = np.where(S.ret_gap<=0.5, S.b_AB, np.nan)
S['b_docAB'] = S.act_doc - S.bm_AB
S['b_docall'] = S.act_doc - S.bm_all
for k,(v,l) in Y.items():
    if v is None: Y[k]=(k,l)
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
COLS = [dict(x='conf_pen_vendor',ctrl=C1+C2+C3,fe='fy',plan='No',year='Yes',lastn=''),
        dict(x='conf_pen_vendor',ctrl=C1+C2+C3+C4+C5,fe='fy',plan='No',year='Yes',lastn=''),
        dict(x='conf_pen_vendor',ctrl=C1+C2+C3+C4+C5,fe='ppd_id',plan='Yes',year='No',lastn=''),
        dict(x='conf_pen_vendor',ctrl=C1+C2+C3+C4+C5,fe='ppd_id + fy',plan='Yes',year='Yes',lastn=''),
        dict(x='last5',ctrl=C1+C2+C3+C4+C5,fe='fy',plan='No',year='Yes',lastn='5'),
        dict(x='last10',ctrl=C1+C2+C3+C4+C5,fe='fy',plan='No',year='Yes',lastn='10')]
RAW = pf.ssc(adj=False, fixef_k='none', cluster_adj=False)
def run(y, col):
    rhs = " + ".join([col['x']]+col['ctrl'])
    fits = {cl: pf.feols(f'{y} ~ {rhs} | {col["fe"]}', data=S, vcov={'CRV1':cl}, ssc=RAW) for cl in ['ppd_id','fy','py']}
    m = fits['ppd_id']; V = np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['py']._vcov)
    N=m._N; names=list(m._coefnames); G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V *= (N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    m_adj = pf.feols(f'{y} ~ {rhs} | {col["fe"]}', data=S, vcov='iid')
    est = {('conf' if n==col['x'] else n):(float(m.coef()[n]), float(np.sqrt(max(V[i,i],0)))) for i,n in enumerate(names)}
    return dict(est=est, N=int(N), G=G, adjr2=float(m_adj._adj_r2), col=col)
RES = {k:[run(v,c) for c in COLS] for k,(v,l) in Y.items()}
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("# Table III rerun with the updated benchmark (benchmarks_with_inferred.csv); Conflicted CIO coefficient (t), SE double clustered by plan and year")
P(f"{'dependent variable':100s} " + " ".join(f"{'('+str(i+1)+')':>18s}" for i in range(6)))
for k,(v,l) in Y.items():
    cells=[]
    for r in RES[k]:
        b,se=r['est']['conf']; t=b/se; p=2*stats.t.sf(abs(t),r['G']-1); cells.append(f"{b:6.3f}{star(p):3s}({t:5.2f})")
    P(f"{l:100s} " + " ".join(f"{c:>18s}" for c in cells))
    P(f"{'   N':100s} " + " ".join(f"{r['N']:>18d}" for r in RES[k]))
P("\nCoverage in Table III sample: original benchmark %d | updated reported %d | updated reported+A/B %d | A/B with PPD-document return agreement %d" % (S.bm_old.notna().sum(), S.bm_rep.notna().sum(), S.bm_AB.notna().sum(), S.b_AB_ok.notna().sum()))
P("Rows where PPD and document returns differ by more than 0.5 pp among rows with the updated benchmark: %d (conflicted %d)" % (int(((S.ret_gap>0.5)&S.bm_AB.notna()).sum()), int(S[(S.ret_gap>0.5)&S.bm_AB.notna()].conf_pen_vendor.sum())))
open('/home/user/PensionData/referee_response/time_to_departure/results_table3_updated_benchmark_v2.md','w').write('\n'.join(out))
pd.to_pickle(dict(RES=RES, Y=Y), 'table3_newbench_res_v2.pkl'); S.to_pickle('table3_newbench_S_v2.pkl')
