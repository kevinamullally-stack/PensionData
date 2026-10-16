exec(open('xsec_setup_v2.py').read())
C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
FULL=C1+C2+C3+C4+C5
FP=pd.read_pickle('df_newbench_v2.pkl')
S=S.merge(FP[['ppd_id','fy','underpaid1','underpaid2']].rename(columns={'underpaid1':'up1','underpaid2':'up2'}),on=['ppd_id','fy'],how='left',validate='1:1')
# rebuilt Underpaid: CIO pay below the median of reported CIO pay that fiscal year (all plan-years in the data)
med=FP.groupby('fy').CIO_TotalComp.median()
S['fy_median_pay']=S.fy.map(med)
S['up_rc_raw']=np.where(S.CIO_TotalComp.isna(),np.nan,(S.CIO_TotalComp<S.fy_median_pay).astype(float))
S['pay_spell']=S.cio.astype(str)+'|'+S.ppd_id.astype(str)
S=S.sort_values(['pay_spell','fy'])
S['up_rc']=S.groupby('pay_spell').up_rc_raw.transform(lambda v: v.ffill().bfill())      # filled like Underpaid
S['spell_has_pay']=S.groupby('pay_spell').CIO_TotalComp.transform(lambda v: v.notna().any())
S=S.sort_values(['ppd_id','fy'])
S['up_paid_spells']=S.underpaid.where(S.spell_has_pay)                                   # Underpaid, spells with reported pay only
S['up_fix']=S.underpaid.where(~((S.underpaid==0)&S.up2.isna()))                          # zeros where underpaid2 is missing -> missing
def run(y, xv):
    d=S.dropna(subset=[y,xv,'conf_pen_vendor','fye_id']+FULL).copy()
    d=d[d.fye_id.map(d.fye_id.value_counts())>1].copy()
    d['conf']=d.conf_pen_vendor; d['X']=d[xv].astype(float); d['confX']=d.conf*d.X
    rhs=['conf','confX','X']+FULL; d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | fye_id'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; assert m._N==len(d)
    V=np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]), int(fits['fy']._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat)
    def lc(wd):
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se; return dict(est=e,se=se,t=t,p=2*stats.t.sf(abs(t),G-1))
    return dict(conf=lc({'conf':1}),confX=lc({'confX':1}),X=lc({'X':1}),sum=lc({'conf':1,'confX':1}),N=int(N),G=G,
                adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2),nconf=int(d.conf.sum()),ncio=d.loc[d.conf==1,'cio'].nunique(),
                share1=float(d.X.mean()), share1_conf=float(d.loc[d.conf==1,'X'].mean()))
UV=[('underpaid','Underpaid (as in the paper)'),
    ('up_fix','Underpaid, 0s with underpaid2 missing set to missing'),
    ('up_paid_spells','Underpaid, spells with reported pay only'),
    ('up_rc','Rebuilt: below annual median pay, filled within spell'),
    ('up_rc_raw','Rebuilt: below annual median pay, reported years only')]
UP={v:{y:run(y,v) for y in ['peer_adj_ret100','b_AB']} for v,_ in UV}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
for v,l in UV:
    for y in ['peer_adj_ret100','b_AB']:
        r=UP[v][y]; print(f"{l[:52]:52s} {y[:6]:6s} conf {r['conf']['est']:6.3f}{st(r['conf']['p']):3s}({r['conf']['t']:5.2f}) | confX {r['confX']['est']:6.3f}{st(r['confX']['p']):3s}({r['confX']['t']:5.2f}) | X=1 {r['sum']['est']:6.3f}{st(r['sum']['p']):3s}({r['sum']['t']:5.2f}) | N {r['N']} conf {r['nconf']} share1 {r['share1']:.2f}/{r['share1_conf']:.2f}")
# agreement table and row-level disagreement list
S['grp']=np.where(S.CIO_TotalComp.notna(),'Pay reported this year',np.where(S.spell_has_pay,'Pay reported in other years of the spell','No pay reported in the spell'))
pd.to_pickle(dict(UP=UP,UV=UV,S=S[['ppd_id','fy','cio','grp','CIO_TotalComp','fy_median_pay','underpaid','up1','up2','up_rc_raw','up_rc','conf_pen_vendor']]),'underpaid_check.pkl')
