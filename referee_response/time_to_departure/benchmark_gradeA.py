exec(open('xsec_setup_v2.py').read())          # S (Table III sample), fye_id, young/highrate/highfund, C1-C3, RAW
C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']; FULL=C1+C2+C3+C4+C5
S['bm_A'] = S.bm_rep.where(S.bm_rep.notna(), S.bm_inf.where(S.grade=='A'))      # reported, else inferred grade A only
S['b_A'] = S.invret100 - S.bm_A
S['b_rep'] = S.invret100 - S.bm_rep
for q in [5,10]:
    S[f'last{q}'] = S.conf_cio.astype(float)
    S.loc[S.year_departs.notna() & (S.conf_cio==1) & (S.fy <= S.year_departs - q), f'last{q}'] = 0.0
# continuous characteristics, as in xsec_interactions_continuous.py
S['log_comp']=np.log(S.CIO_TotalComp)
S['log_comp_rel']=S.log_comp-S.groupby('fy').log_comp.transform('mean')
S['pay_spell']=S.cio.astype(str)+'|'+S.ppd_id.astype(str)
S=S.sort_values(['pay_spell','fy']); S['rel_pay_f']=S.groupby('pay_spell').log_comp_rel.transform(lambda v: v.ffill().bfill()); S=S.sort_values(['ppd_id','fy'])
YS=[('b_AB','Reported + inferred grade A/B (current)'),('b_A','Reported + inferred grade A only'),('b_rep','Reported benchmarks only')]
def fit(y, rhs, fe, center=None, lcs=()):
    d=S.dropna(subset=[y]+[r for r in rhs if r in S]+[c for c in (center or {})]).copy()
    if fe=='fye_id': d=d[d.fye_id.map(d.fye_id.value_counts())>1].copy()
    return d
def reg(y, xcol, ctrl, fe, X=None, center=False):
    need=[y,xcol]+ctrl+([X] if X else [])+fe.replace(' ','').split('+')
    d=S.dropna(subset=need).copy()
    for g in fe.replace(' ','').split('+'):                      # drop singleton FE groups as reghdfe does (one pass suffices here)
        d=d[d[g].map(d[g].value_counts())>1].copy()
    d['conf']=d[xcol]; rhs=['conf']+ctrl; extra={}
    if X:
        xs=d[X].astype(float); m_=xs.mean() if center else 0.0
        def sp(x,p):
            x=np.sort(np.asarray(x)); n=len(x); P=n*p/100
            return (x[int(P)-1]+x[int(P)])/2 if float(P).is_integer() else x[int(np.floor(P))]
        d['X']=xs-m_; d['confX']=d.conf*d.X; rhs=['conf','confX','X']+ctrl
        extra=dict(p25=sp(xs,25)-m_, p75=sp(xs,75)-m_)
    d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | {fe}'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; assert m._N==len(d), (m._N,len(d))
    V=np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]),int(fits['fy']._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat)
    def lc(wd):
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se; return dict(est=e,se=se,t=t,p=2*stats.t.sf(abs(t),G-1))
    out=dict(conf=lc({'conf':1}),N=int(N),G=G,adjr2=float(pf.feols(f,data=d,vcov='iid')._adj_r2),nconf=int(d.conf.sum()))
    if X:
        out.update(confX=lc({'confX':1}),X=lc({'X':1}),sum=lc({'conf':1,'confX':1}),p25=lc({'conf':1,'confX':extra['p25']}),p75=lc({'conf':1,'confX':extra['p75']}))
    return out
# Table III, Panel B columns (1)-(6)
T3COLS=[('conf_pen_vendor',C1+C2+C3,'fy'),('conf_pen_vendor',FULL,'fy'),('conf_pen_vendor',FULL,'ppd_id'),('conf_pen_vendor',FULL,'ppd_id + fy'),('last5',FULL,'fy'),('last10',FULL,'fy')]
T3={y:[reg(y,x,c,fe) for x,c,fe in T3COLS] for y,_ in YS}
# Interactions: all controls + fye1 FE
XB=[('underpaid','Underpaid'),('young','Young CIO'),('prior_private_exp','Prior Private Exp.'),('fincenter1','Financial Center'),('highrate','High Discount Rate'),('highfund','High Funding')]
XC=[('log_comp','Log CIO Total Comp.',FULL),('rel_pay_f','Relative CIO Pay (filled)',FULL),('cio_age','CIO Age',[c for c in FULL if c!='l_log_cio_age'])]
INT={y:{**{xv:reg(y,'conf_pen_vendor',[c for c in FULL if c!=xv],'fye_id',X=xv) for xv,_ in XB},
        **{xv:reg(y,'conf_pen_vendor',ctl,'fye_id',X=xv,center=True) for xv,_,ctl in XC}} for y,_ in YS}
# correlations with the peer-adjusted return
COR={}
for y,_ in YS:
    d=S.dropna(subset=[y,'peer_adj_ret100']); dm=d[[y,'peer_adj_ret100']]-d.groupby('fye1')[[y,'peer_adj_ret100']].transform('mean')
    COR[y]=dict(N=len(d),pearson=d[y].corr(d.peer_adj_ret100),spearman=d[y].corr(d.peer_adj_ret100,method='spearman'),within=dm[y].corr(dm.peer_adj_ret100),
                conf=d[d.conf_pen_vendor==1][y].corr(d[d.conf_pen_vendor==1].peer_adj_ret100),nonconf=d[d.conf_pen_vendor==0][y].corr(d[d.conf_pen_vendor==0].peer_adj_ret100))
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
print('coverage:', {y:int(S[y].notna().sum()) for y,_ in YS}, '| conflicted:', {y:int(S.loc[S[y].notna(),'conf_pen_vendor'].sum()) for y,_ in YS}, '| grade B rows', int((S.bm_rep.isna()&(S.grade=='B')).sum()), 'conflicted', int((S.bm_rep.isna()&(S.grade=='B')&(S.conf_pen_vendor==1)).sum()))
for y,l in YS: print('corr', l, {k:(round(v,3) if isinstance(v,float) else v) for k,v in COR[y].items()})
print('\nTable III Panel B')
for y,l in YS: print(f"{l[:42]:42s}", ' '.join(fm(r['conf']) for r in T3[y]), '| N', [r['N'] for r in T3[y]])
print('\nInteractions (all controls + fye1): Conflicted x X')
for xv,xl in XB+[(a,b) for a,b,_ in XC]:
    print(f"{xl:28s}", ' | '.join(f"{fm(INT[y][xv]['confX'])} N {INT[y][xv]['N']}" for y,_ in YS))
pd.to_pickle(dict(T3=T3,INT=INT,COR=COR,YS=YS,XB=XB,XC=[(a,b) for a,b,_ in XC]),'gradeA_res.pkl')
