src=open('halves_v3.py').read().split("R={}")[0]; exec(src)      # df, S (Table III sample) with second, ten_dep, cp
from scipy.stats import ttest_ind, ttest_1samp, wilcoxon, mannwhitneyu, trim_mean
import statsmodels.api as sm
D=S[(S.curr==0)&S.second.notna()].copy(); D['conf']=D.conf_pen_vendor.astype(float)
for y in ['peer_adj_ret100','b_AB']:
    D[y+'_dm']=D[y]-S.groupby('fye_id')[y].transform('mean').reindex(D.index)      # net of the same fiscal-year-end mean (Table III sample)
YS=[('peer_adj_ret100','Peer-Adjusted Return'),('b_AB','Benchmark-Adjusted Return')]
def unit_diffs(y, unit, minten=0):
    d=D[(D.ten_dep>=minten)].dropna(subset=[y])
    if unit=='spell':
        h=d.groupby(['cp','second'])[y].mean().unstack(); n=d.groupby('cp').size(); c=d.groupby('cp').conf.max(); pid=d.groupby('cp').ppd_id.first()
    else:   # one observation per CIO: average across plans within CIO-year, then within half
        dd=d.groupby(['cio','fy','second'],as_index=False).agg(v=(y,'mean'),conf=('conf','max'),ppd_id=('ppd_id','first'))
        h=dd.groupby(['cio','second']).v.mean().unstack(); n=dd.groupby('cio').size(); c=dd.groupby('cio').conf.max(); pid=dd.groupby('cio').ppd_id.first()
    T=pd.DataFrame({'d':h[1.0]-h[0.0],'n':n,'conf':c,'ppd_id':pid}).dropna(subset=['d'])
    return T
def tests(T, drop=0, side=None):
    if drop:
        cc=T[T.conf==1].d.sort_values()
        out_idx=cc.index[:drop] if side=='neg' else cc.index[-drop:]
        T=T.drop(index=out_idx)
    a=T[T.conf==1].d; b=T[T.conf==0].d
    out=dict(nc=len(a),no=len(b),mc=a.mean(),mo=b.mean(),diff=a.mean()-b.mean(),
             p1c=ttest_1samp(a,0).pvalue,p1o=ttest_1samp(b,0).pvalue,p=ttest_ind(a,b).pvalue,pw=ttest_ind(a,b,equal_var=False).pvalue,
             medc=a.median(),medo=b.median(),psr=wilcoxon(a).pvalue if len(a)>0 else np.nan,prs=mannwhitneyu(a,b).pvalue,
             tm=trim_mean(a,0.1)-trim_mean(b,0.1),negc=float((a<0).mean()),nego=float((b<0).mean()),sdc=a.std(),sdo=b.std())
    X=sm.add_constant(T.conf); m=sm.WLS(T.d,X,weights=T.n).fit(cov_type='cluster',cov_kwds={'groups':T.ppd_id}); out['wdiff']=m.params['conf']; out['wp']=m.pvalues['conf']
    return out
R={}
for y,_ in YS:
    for unit in ['spell','cio']:
        R[(y,unit,'base')]=tests(unit_diffs(y,unit))
        R[(y,unit,'ten4')]=tests(unit_diffs(y,unit,4))
        R[(y,unit,'dm')]=tests(unit_diffs(y+'_dm',unit))
        T=unit_diffs(y,unit)
        for k in [3,5]:
            R[(y,unit,f'dropneg{k}')]=tests(T,k,'neg'); R[(y,unit,f'droppos{k}')]=tests(T,k,'pos')
# spell-level return slopes (parallel to the Fee Slope), at least 3 years, winsorized 1/99
SL={}
for y,_ in YS:
    rows=[]
    for cp,g in S[S.curr==0].dropna(subset=[y]).groupby('cp'):
        if g.fy.nunique()<3: continue
        rows.append(dict(slope=np.polyfit(g.fy.astype(float),g[y].astype(float),1)[0],n=len(g),conf=float(g.conf_pen_vendor.iloc[0]),ppd_id=g.ppd_id.iloc[0]))
    T=pd.DataFrame(rows); lo,hi=T.slope.quantile([.01,.99]); T['d']=T.slope.clip(lo,hi)
    SL[y]=tests(T)
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
for y,yl in YS:
    print(f"\n######## {yl}: second-half mean minus first-half mean, equal weight per unit")
    for unit in ['spell','cio']:
        for k,lab in [('base','all'),('ten4','tenure at departure >= 4'),('dm','net of fiscal-year-end mean'),('dropneg3','drop 3 most negative conflicted'),('droppos3','drop 3 most positive conflicted'),('dropneg5','drop 5 most negative'),('droppos5','drop 5 most positive')]:
            r=R[(y,unit,k)]
            print(f"  [{unit:5s}] {lab:34s} conf {r['mc']:+.3f} (p0 {r['p1c']:.3f}; median {r['medc']:+.3f}, SR p {r['psr']:.3f}; n {r['nc']}) | other {r['mo']:+.3f} (p0 {r['p1o']:.3f}; n {r['no']}) | diff {r['diff']:+.3f}{st(r['p'])} p {r['p']:.3f} Welch {r['pw']:.3f} rank {r['prs']:.3f} trim {r['tm']:+.3f} | wtd {r['wdiff']:+.3f} p {r['wp']:.3f} | share neg {r['negc']:.2f}/{r['nego']:.2f}")
    r=SL[y]; print(f"  [slope] conf {r['mc']:+.4f} other {r['mo']:+.4f} diff {r['diff']:+.4f}{st(r['p'])} p {r['p']:.3f} Welch {r['pw']:.3f} | medians {r['medc']:+.4f} vs {r['medo']:+.4f} rank p {r['prs']:.3f} | wtd {r['wdiff']:+.4f} p {r['wp']:.3f} | n {r['nc']}/{r['no']}")
pd.to_pickle(dict(R=R,SL=SL,YS=YS),'ret_halves_ew.pkl')
