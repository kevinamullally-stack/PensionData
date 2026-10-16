exec(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'xsec_setup_v2.py')).read())
C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
for q in [5,10]:
    S[f'last{q}'] = S.conf_cio.astype(float)
    S.loc[S.year_departs.notna() & (S.conf_cio==1) & (S.fy <= S.year_departs - q), f'last{q}'] = 0.0
COLS = [dict(x='conf_pen_vendor',ctrl=C1+C2+C3,fe='fye_id',plan='No',ctl='Base',lastn=''),
        dict(x='conf_pen_vendor',ctrl=C1+C2+C3+C4+C5,fe='fye_id',plan='No',ctl='All',lastn=''),
        dict(x='conf_pen_vendor',ctrl=C1+C2+C3+C4+C5,fe='ppd_id + fye_id',plan='Yes',ctl='All',lastn=''),
        dict(x='last5',ctrl=C1+C2+C3+C4+C5,fe='fye_id',plan='No',ctl='All',lastn='5'),
        dict(x='last10',ctrl=C1+C2+C3+C4+C5,fe='fye_id',plan='No',ctl='All',lastn='10')]
XV = [('underpaid','underpaid','Underpaid'),('young','young','Young CIO'),('priv','prior_private_exp','Prior Private Exp.'),
      ('fin','fincenter1','Financial Center'),('rate','highrate','High Discount Rate'),('fund','highfund','High Funding')]
YS = [('peer_adj_ret100','Peer-adjusted return'),('b_AB','Benchmark-adjusted return, updated benchmark'),('bench_adj_ret_pct','Benchmark-adjusted return, original benchmark'),('b_docAB','Benchmark-adjusted return, updated benchmark, document-matched return')]
def run(y, xv, col):
    d = S.dropna(subset=[xv]).copy()
    d['conf'] = d[col['x']]; d['confX'] = d.conf*d[xv]; d['X'] = d[xv].astype(float)
    ctrl = [c for c in col['ctrl'] if c != xv]                 # the cross-sectional variable enters once, as X
    rhs = ['conf','confX','X'] + ctrl
    d['_int'] = d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f = f'{y} ~ {" + ".join(rhs)} | {col["fe"]}'
    fits = {c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m = fits['ppd_id']; V = np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]), int(fits['fy']._G[0])); K=len(names)+1
    V *= (N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2)
    if w.min()<0: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat)
    def lc(wd):
        if any(k not in names for k in wd): return dict(est=np.nan,se=np.nan,t=np.nan,p=np.nan)
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se if se>0 else np.nan; p=2*stats.t.sf(abs(t),G-1) if se>0 else np.nan
        return dict(est=e,se=se,t=t,p=p)
    madj = pf.feols(f, data=d, vcov='iid')
    return dict(conf=lc({'conf':1}), confX=lc({'confX':1}), X=lc({'X':1}), sum=lc({'conf':1,'confX':1}), N=int(N), G=G, adjr2=float(madj._adj_r2), col=col)
RES = {k:{y:[run(y,xv,c) for c in COLS] for y,_ in YS} for k,xv,_ in XV}
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f(r): return "      n/a      " if np.isnan(r['est']) else f"{r['est']:6.3f}{star(r['p']):3s}({r['t']:5.2f})"
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("# Table III with Conflicted CIO interacted with each cross-sectional variable (controls common to both groups); fiscal-year-end date (fye1) fixed effects. SE double clustered by plan and year; t in parentheses.")
for k,xv,xl in XV:
    P(f"\n## {xl}")
    for y,yl in YS[:2]:
        P(f"### {yl}")
        P(f"{'':38s} " + " ".join(f"{'('+str(i+1)+')':>17s}" for i in range(len(COLS))))
        for term,tl in [('conf','Conflicted CIO'),('confX',f'Conflicted CIO x {xl}'),('X',xl),('sum',f'Conflicted CIO, {xl} = 1')]:
            P(f"{tl:38s} " + " ".join(f"{f(r[term]):>17s}" for r in RES[k][y]))
        P(f"{'N':38s} " + " ".join(f"{r['N']:>17d}" for r in RES[k][y]))
P("\n# Summary: interaction coefficient (Conflicted CIO x variable) for all four performance measures, columns (1)-(5)")
for k,xv,xl in XV:
    for y,yl in YS:
        P(f"{xl:20s} {yl[:62]:62s} " + " ".join(f"{f(r['confX']):>17s}" for r in RES[k][y]))
open('/home/user/PensionData/referee_response/time_to_departure/results_xsec_interactions_fye1.md','w').write('\n'.join(out))
pd.to_pickle(dict(RES=RES, XV=XV, YS=YS), 'interact_res_fye1.pkl')
