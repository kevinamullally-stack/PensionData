exec(open('xsec_setup_v2.py').read())
C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
FULL = C1+C2+C3+C4+C5
S['log_comp'] = np.log(S.CIO_TotalComp)
S = S.sort_values(['ppd_id','fy'])
# prior-year pay from the full panel, as Stata's l. operator does (the prior year can lie outside the Table III sample)
FP = pd.read_pickle('df_newbench_v2.pkl')[['ppd_id','fy','CIO_TotalComp']].sort_values(['ppd_id','fy'])
FP['l_log_comp'] = np.where(FP.groupby('ppd_id').fy.diff()==1, np.log(FP.groupby('ppd_id').CIO_TotalComp.shift(1)), np.nan)
S = S.merge(FP[['ppd_id','fy','l_log_comp']], on=['ppd_id','fy'], how='left', validate='1:1')
S['log_comp_rel'] = S.log_comp - S.groupby('fy').log_comp.transform('mean')     # pay relative to the same fiscal year
# relative pay filled within the CIO's spell at the plan: carry the nearest earlier reported year forward,
# and the first reported year back (mirrors the backfilled underpaid measure)
S['pay_spell'] = S.cio.astype(str)+'|'+S.ppd_id.astype(str)
S = S.sort_values(['pay_spell','fy'])
S['rel_pay_f'] = S.groupby('pay_spell').log_comp_rel.transform(lambda v: v.ffill().bfill())
S = S.sort_values(['ppd_id','fy'])
def spct(x, p):   # Stata summarize, detail percentile definition
    x=np.sort(np.asarray(x)); n=len(x); P=n*p/100
    return (x[int(P)-1]+x[int(P)])/2 if float(P).is_integer() else x[int(np.floor(P))]
def run(y, xv, extra=(), drop=(), need=()):
    ctl = [c for c in FULL if c not in drop]
    rhs0 = ['conf_pen_vendor', xv] + ctl + [e for e in extra] + list(need)
    d = S.dropna(subset=[y]+rhs0+['fye_id']).copy()
    d = d[d.fye_id.map(d.fye_id.value_counts())>1].copy()     # reghdfe drops singleton FE groups; so does pyfixest
    m_, p25, p75 = d[xv].mean(), spct(d[xv],25), spct(d[xv],75)
    d['conf']=d.conf_pen_vendor; d['X']=d[xv]-m_; d['confX']=d.conf*d.X
    for e in extra: d['conf_'+e]=d.conf*(d[e]-d[e].mean())    # centered so 'conf' stays the effect at mean pay and mean size
    rhs=['conf','confX','X']+ctl+['conf_'+e for e in extra]
    d['_int']=d.ppd_id.astype(str)+'#'+d.fy.astype(str)
    f=f'{y} ~ {" + ".join(rhs)} | fye_id'
    fits={c: pf.feols(f, data=d, vcov={'CRV1':c}, ssc=RAW) for c in ['ppd_id','fy','_int']}
    m=fits['ppd_id']; assert m._N==len(d)
    V=np.asarray(fits['ppd_id']._vcov)+np.asarray(fits['fy']._vcov)-np.asarray(fits['_int']._vcov)
    names=list(m._coefnames); N=m._N; G=min(int(fits['ppd_id']._G[0]), int(fits['fy']._G[0])); K=len(names)+1
    V*=(N-1)/(N-K)*G/(G-1); w,Q=np.linalg.eigh((V+V.T)/2); psd=w.min()<0
    if psd: V=(Q*np.clip(w,0,None))@Q.T
    b=np.asarray(m._beta_hat)
    def lc(wd):
        c=np.zeros(len(names))
        for k,v in wd.items(): c[names.index(k)]=v
        e=float(c@b); se=float(np.sqrt(max(c@V@c,0))); t=e/se; return dict(est=e,se=se,t=t,p=2*stats.t.sf(abs(t),G-1))
    madj=pf.feols(f, data=d, vcov='iid')
    return dict(conf=lc({'conf':1}), confX=lc({'confX':1}), X=lc({'X':1}),
                p25=lc({'conf':1,'confX':p25-m_}), p75=lc({'conf':1,'confX':p75-m_}),
                ext={e:lc({'conf_'+e:1}) for e in extra},
                mean=m_, p25v=p25, p75v=p75, sd=d[xv].std(), N=int(N), G=G, adjr2=float(madj._adj_r2),
                nconf=int(d.conf.sum()), ncio=d.loc[d.conf==1,'cio'].nunique(), psd=psd)
YS=[('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark'),('bench_adj_ret_pct','Benchmark-adjusted, original benchmark'),('b_docAB','Benchmark-adjusted, updated, document-matched')]
VAR=[('main','log_comp',(),'Log CIO total comp (same year), centered'),
     ('lag','l_log_comp',(),'Lagged log CIO total comp'),
     ('rel','log_comp_rel',(),'Log comp minus fiscal-year mean (relative pay)'),
     ('size','log_comp',('size',),'Log comp, also Conflicted x Size'),
     ('relf','rel_pay_f',(),'Relative pay, filled within CIO spell'),
     ('relf_size','rel_pay_f',('size',),'Relative pay filled, plus Conflicted x Size'),
     ('up_on_relf','underpaid',(),'CHECK: underpaid (binary) on the filled-pay sample'),
     ('age','cio_age',(),'CIO age in years (same year), centered; lagged log age control dropped'),
     ('age_keep','cio_age',(),'CIO age, lagged log age control kept')]
DROP={'age':('l_log_cio_age',)}
NEED={'up_on_relf':('rel_pay_f',)}
COMP={v:{y:run(y,xv,ex,DROP.get(v,()),NEED.get(v,())) for y,_ in YS} for v,xv,ex,_ in VAR}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:7.3f}{st(r['p']):3s}({r['t']:5.2f})"
print('cio_age in sample:', int(S.cio_age.notna().sum()), 'of', len(S), '| corr(cio_age, exp(l_log_cio_age))', round(S.cio_age.corr(np.exp(S.l_log_cio_age)),3))
for v,xv,ex,vl in VAR:
    print(f"\n## {vl}")
    for y,yl in YS:
        r=COMP[v][y]
        print(f"{yl[:40]:40s} conf@mean {fm(r['conf'])} | confX {fm(r['confX'])} | X {fm(r['X'])} | @p25 {fm(r['p25'])} | @p75 {fm(r['p75'])} | N {r['N']} conf {r['nconf']} CIOs {r['ncio']} | mean {r['mean']:.3f} p25 {r['p25v']:.3f} p75 {r['p75v']:.3f} psd {r['psd']}")
pd.to_pickle(dict(COMP=COMP,VAR=VAR,YS=YS),'interact_comp_res.pkl')
