import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
# Table III with Conflicted CIO split into the first and second half of the CIO's tenure at the plan
d = pd.read_pickle('df_newbench_v2.pkl').sort_values(['ppd_id','fy']).copy()
# halves over all plan-years of the CIO at the plan (as Stata's bysort cio ppd_id), same as halves_v3_fye1
d['cp']=d.cio.astype(str)+'|'+d.ppd_id.astype(str); g=d.groupby('cp')
d['last_fy']=g.fy.transform('max'); d['max_ten']=g.cio_tenure.transform('max')
d['ydep']=d.year_departs; d.loc[d.ydep.isna()&(d.curr==0),'ydep']=d.last_fy
d['ten_dep']=d.max_ten+(d.ydep-d.last_fy).clip(lower=0)
ok=d.cio_tenure.notna()&d.ten_dep.notna()&(d.ten_dep>0)
d['second']=np.where(ok,(d.cio_tenure>d.ten_dep/2).astype(float),np.nan)
d['py']=d.ppd_id.astype(int)*10000+d.fy.astype(int); d['fye_id']=d.fye1.astype(str)
d['b_AB']=d.investmentreturn_1yr*100-d.bm_AB
S=d[(d.cio_dum==1)&(d.fy<=2020)&(d.curr1==0)].copy()
for q in [5,10]:
    S[f'last{q}']=S.conf_cio.astype(float)
    S.loc[S.year_departs.notna()&(S.conf_cio==1)&(S.fy<=S.year_departs-q),f'last{q}']=0.0
for x in ['conf_pen_vendor','last5','last10']:
    S[x+'_h1']=((S[x]==1)&(S.second==0)).astype(float); S[x+'_h2']=((S[x]==1)&(S.second==1)).astype(float); S[x+'_hu']=((S[x]==1)&S.second.isna()).astype(float)
    print(f"{x}: conflicted rows {int(S[x].sum())} = first {int(S[x+'_h1'].sum())} + second {int(S[x+'_h2'].sum())} + undefined {int(S[x+'_hu'].sum())}")
C1=['l_invret','size','l_fund']; C2=['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
C4n=['prior_private_exp','Elite_inst']
def cols(fe_y, c4):
    full=C1+C2+C3+c4+C5
    return [dict(x='conf_pen_vendor',ctrl=C1+C2+C3,fe=fe_y,plan='No',year='Yes',lastn=''),
            dict(x='conf_pen_vendor',ctrl=full,fe=fe_y,plan='No',year='Yes',lastn=''),
            dict(x='conf_pen_vendor',ctrl=full,fe='ppd_id',plan='Yes',year='No',lastn=''),
            dict(x='conf_pen_vendor',ctrl=full,fe='ppd_id + '+fe_y,plan='Yes',year='Yes',lastn=''),
            dict(x='last5',ctrl=full,fe=fe_y,plan='No',year='Yes',lastn='5'),
            dict(x='last10',ctrl=full,fe=fe_y,plan='No',year='Yes',lastn='10')]
VERS={'fy':cols('fy',C4),'fye':cols('fye_id',C4),'fy_noten':cols('fy',C4n)}
RAW=pf.ssc(adj=False,fixef_k='none',cluster_adj=False)
def run(y,col):
    x=col['x']; xs=[x+'_h1',x+'_h2']+([x+'_hu'] if S[x+'_hu'].sum()>0 else [])
    rhs=' + '.join(xs+col['ctrl'])
    fits={cl:pf.feols(f'{y} ~ {rhs} | {col["fe"]}',data=S,vcov={'CRV1':cl},ssc=RAW) for cl in ['ppd_id','fy','py']}
    m=fits['ppd_id']; V=np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['py']._vcov)
    N=m._N; names=list(m._coefnames); G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat); ren={x+'_h1':'h1',x+'_h2':'h2',x+'_hu':'hu'}
    est={ren.get(n,n):(float(b[i]),float(np.sqrt(max(V[i,i],0)))) for i,n in enumerate(names)}
    c=np.zeros(len(names)); c[names.index(x+'_h2')]=1; c[names.index(x+'_h1')]=-1
    dd=float(c@b); se=float(np.sqrt(max(c@V@c,0)))
    adj=float(pf.feols(f'{y} ~ {rhs} | {col["fe"]}',data=S,vcov='iid')._adj_r2)
    return dict(est=est,diff=(dd,se),N=int(N),G=G,adjr2=adj,col=col)
YS=[('peer_adj_ret100','Peer-Adjusted Return'),('b_AB','Benchmark-Adjusted Return')]
RES={(v,y):[run(y,c) for c in VERS[v]] for v in VERS for y,_ in YS}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def pv(b,se,G): t=b/se; return t,2*stats.t.sf(abs(t),G-1)
for v in VERS:
    for y,yl in YS:
        print(f"\n[{v}] {yl}")
        for k,l in [('h1','Conf x First'),('h2','Conf x Second')]:
            print(f"  {l:14s} "+' '.join(f"{r['est'][k][0]:7.3f}{st(pv(*r['est'][k],r['G'])[1]):3s}({pv(*r['est'][k],r['G'])[0]:5.2f})" for r in RES[(v,y)]))
        print(f"  {'Second-First':14s} "+' '.join(f"{r['diff'][0]:7.3f}{st(pv(*r['diff'],r['G'])[1]):3s}(p{pv(*r['diff'],r['G'])[1]:.2f})" for r in RES[(v,y)]))
        print(f"  {'N':14s} "+' '.join(f"{r['N']:>17d}" for r in RES[(v,y)]))
NC={x:dict(h1=int(S[x+'_h1'].sum()),h2=int(S[x+'_h2'].sum()),hu=int(S[x+'_hu'].sum())) for x in ['conf_pen_vendor','last5','last10']}
pd.to_pickle(dict(RES=RES,YS=YS,NC=NC),'table3_conflicted_halves.pkl')
