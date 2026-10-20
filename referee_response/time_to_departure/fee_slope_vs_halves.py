src=open('halves_v3.py').read().split("R={}")[0]; exec(src)            # df (with second, ten_dep, cp), S (Table III sample), fit(), controls
import statsmodels.api as sm
D=S[S.curr==0].copy()                                                    # CIOs who have left (conflicted and others), Table III sample
D['fee']=D.fee_ratio_pct; D['conf']=D.conf_pen_vendor.astype(float)
D['fee_dm']=D.fee-D.groupby('fy').fee.transform('mean')                 # fee net of the sample-wide fiscal-year mean
def slopes(var, minobs):
    rows=[]
    for cp,g in D.dropna(subset=[var]).groupby('cp'):
        if g.fy.nunique()<minobs: continue
        b=np.polyfit(g.fy.astype(float),g[var].astype(float),1)[0]
        rows.append(dict(cp=cp,slope=b,n=len(g),conf=float(g.conf.iloc[0]),ppd_id=g.ppd_id.iloc[0],
                         gap=(g.loc[g.second==1,'fy'].mean()-g.loc[g.second==0,'fy'].mean()) if g.second.notna().all() and g.second.nunique()==2 else np.nan))
    T=pd.DataFrame(rows)
    lo,hi=T.slope.quantile([.01,.99]); T['slope_w']=T.slope.clip(lo,hi)      # winsorized 1/99
    return T
def ttest(T,col='slope_w'):
    a=T.loc[T.conf==1,col]; b=T.loc[T.conf==0,col]; t,p=stats.ttest_ind(a,b)
    return dict(conf=a.mean(),oth=b.mean(),diff=a.mean()-b.mean(),p=p,nc=len(a),no=len(b))
def wls(T,col='slope_w'):
    X=sm.add_constant(T.conf); m=sm.WLS(T[col],X,weights=T.n).fit(cov_type='cluster',cov_kwds={'groups':T.ppd_id})
    return dict(diff=m.params['conf'],p=m.pvalues['conf'],conf=m.params['const']+m.params['conf'],oth=m.params['const'])
OUT={}
# 1. spell-level slope t-tests (the Fee Slope construction, no allocation controls)
for nm,var,mo in [('base2','fee',2),('base3','fee',3),('dm3','fee_dm',3)]:
    T=slopes(var,mo); OUT[('slope',nm)]=ttest(T); OUT[('slope_w',nm)]=wls(T)
    if nm=='base3': T3=T
# 2. by minimum spell length
for mo in [4,6,8]:
    T=slopes('fee',mo); OUT[('slope',f'min{mo}')]=ttest(T); OUT[('slope_w',f'min{mo}')]=wls(T)
# 3. slope by spell length bucket
T3['len']=pd.cut(T3.n,[2,3,5,8,30],labels=['3','4-5','6-8','9+'])
BYLEN=T3.groupby(['len','conf']).slope_w.agg(['mean','count']).unstack()
# 4. pooled within-spell trend (observation-weighted): fee ~ conf x year + spell FE (+ year FE)
D['t']=D.fy.astype(float)-2010; D['conf_t']=D.conf*D.t
OUT['pool_noyear']=fit('fee',['t','conf_t'],'cp',D,{'b':{'conf_t':1}})
OUT['pool_year']=fit('fee',['conf_t'],'cp + fye_id',D,{'b':{'conf_t':1}})
# 5. halves within spell, conflicted vs other departing CIOs: fee ~ second + conf x second + spell FE + year FE
H=D[D.second.notna()].copy(); H['conf_second']=H.conf*H.second
OUT['halves_noyear']=fit('fee',['second','conf_second'],'cp',H,{'b':{'conf_second':1},'oth':{'second':1},'cnf':{'second':1,'conf_second':1}})
OUT['halves_year']=fit('fee',['second','conf_second'],'cp + fye_id',H,{'b':{'conf_second':1},'oth':{'second':1},'cnf':{'second':1,'conf_second':1}})
# 6. implied second-minus-first gap from each conflicted spell's slope
Tc=T3[(T3.conf==1)&T3.gap.notna()].copy(); Tc['implied']=Tc.slope_w*Tc.gap
IMPL=dict(eq=float(Tc.implied.mean()),w=float(np.average(Tc.implied,weights=Tc.n)),gap=float(Tc.gap.mean()),n=len(Tc))
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
print("Sample: departed CIOs in the Table III sample with fee data;", D.fee.notna().sum(), "plan-years,", D.dropna(subset=['fee']).cp.nunique(), "spells")
print("\n1-2. Spell-level slope (pp/yr), winsorized: equal-weighted t-test | weighted by spell observations")
for k in ['base2','base3','dm3','min4','min6','min8']:
    a=OUT[('slope',k)]; w=OUT[('slope_w',k)]
    print(f"  {k:6s} conf {a['conf']:.4f} oth {a['oth']:.4f} diff {a['diff']:+.4f}{st(a['p'])} (p {a['p']:.3f}; n {a['nc']}/{a['no']}) | weighted diff {w['diff']:+.4f} (p {w['p']:.3f})")
print("\n3. Mean slope by spell length (min 3 obs):\n", BYLEN.round(4).to_string())
for k,l in [('pool_noyear','pooled trend, spell FE'),('pool_year','pooled trend, spell + FYE FE'),('halves_noyear','halves DiD, spell FE'),('halves_year','halves DiD, spell + FYE FE')]:
    r=OUT[k]['b']; print(f"  {l:32s} conflicted extra: {r['est']:+.4f}{st(r['p'])} (t {r['t']:.2f}, p {r['p']:.3f}) N {OUT[k]['N']}")
for k in ['halves_noyear','halves_year']: print(f"  {k}: second-half change, others {OUT[k]['oth']['est']:+.4f} (p {OUT[k]['oth']['p']:.3f}); conflicted {OUT[k]['cnf']['est']:+.4f} (p {OUT[k]['cnf']['p']:.3f})")
print(f"\n6. Implied conflicted second-minus-first gap from spell slopes: equal-weighted {IMPL['eq']:.4f}, observation-weighted {IMPL['w']:.4f} (mean year gap between halves {IMPL['gap']:.2f}, {IMPL['n']} spells)")
pd.to_pickle(dict(OUT=OUT,BYLEN=BYLEN,IMPL=IMPL,nD=int(D.fee.notna().sum()),nsp=D.dropna(subset=['fee']).cp.nunique()),'fee_reconcile.pkl')

# medians, rank tests, short-spell interaction (saved for the workbook)
from scipy.stats import mannwhitneyu
MED={}
for mo in [3,6]:
    T=slopes('fee',mo); a=T[T.conf==1].slope; b=T[T.conf==0].slope
    MED[mo]=dict(mc=float(a.median()),mo_=float(b.median()),p=float(mannwhitneyu(a,b).pvalue),pc=float(np.mean(a>0)),po=float(np.mean(b>0)))
H3=pd.read_pickle('halves_v3.pkl')['R']
pd.to_pickle(dict(OUT=OUT,BYLEN=BYLEN,IMPL=IMPL,MED=MED,HV=dict(fye=H3[('split','fye','fee_ratio_pct')]['diff'],plan=H3[('split','plan','fee_ratio_pct')]['diff']),
                  nD=int(D.fee.notna().sum()),nsp=D.dropna(subset=['fee']).cp.nunique()),'fee_reconcile.pkl')
