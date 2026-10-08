"""Time-to-departure / dose-response analysis for the "Conflicted CIOs" revision.

Usage:  python3 ttd_analysis.py /path/to/data_v3_3.dta
Writes results_full.md and df_built.pkl next to this script. See memo.md for the write-up.
Requires: pandas, pyfixest, scipy.
"""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
import sys, os
DATA = sys.argv[1] if len(sys.argv) > 1 else 'data_v3_3.dta'
OUT = os.path.dirname(os.path.abspath(__file__))
def load():
    df = pd.read_stata(DATA, convert_categoricals=False).copy()
    df['spell'] = df.groupby(['ppd_id','cio']).ngroup()
    df['departs_obs'] = df.year_departs.notna().astype(int)
    df['other_dep'] = ((df.departs_obs==1)&(df.conf_cio==0)).astype(int)
    df['ttd'] = df.time_to_departure.astype(int)
    df['last_fy'] = df.groupby('spell').fy.transform('max')
    df['censored'] = ((df.departs_obs==0)&(df.last_fy==2020)).astype(int)
    df['unknown_exit'] = ((df.departs_obs==0)&(df.last_fy<2020)).astype(int)
    return df
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300); pd.set_option('display.max_columns', 40)

df = load()
df['ret100'] = df.peer_adj_ret*100; df['bret100'] = df.bench_adj_ret*100
df['fee100'] = df.total_fee_pct*100; df['expr100'] = df.exp_ratio*100
for a in ['pe','re','hf','eq','fi']: df[f'{a}fee100'] = df[f'{a}_fee_pct']*100
df['alt_actl'] = df.PETotal_Actl + df.HFTotal_Actl + df.RETotal_Actl + df.AltMiscTotal_Actl
# --- departure types
df['dep_type'] = np.select([df.conf_cio==1, (df.conf_cio==0)&(df.departs_obs==1), df.unknown_exit==1, df.censored==1],
                           ['conf','other','unknown','censored'], default='na')
# bins of years to departure (only for conf / other observed departures)
def binlab(t):
    if t <= -5: return 'm5'
    return {-4:'m4',-3:'m3',-2:'m2',-1:'m1',0:'p0'}.get(t, 'na')
df['bin'] = df.ttd.apply(binlab)
BINS = ['m5','m4','m3','m2','m1','p0']
for b in BINS:
    df[f'c_{b}'] = ((df.dep_type=='conf')&(df['bin']==b)).astype(int)
    df[f'o_{b}'] = ((df.dep_type=='other')&(df['bin']==b)).astype(int)
# coarse: far (<=-4), mid (-3,-2), near (-1,0)
df['c_far']=((df.dep_type=='conf')&(df.ttd<=-4)).astype(int); df['c_mid']=((df.dep_type=='conf')&(df.ttd.isin([-3,-2]))).astype(int); df['c_near']=((df.dep_type=='conf')&(df.ttd>=-1)).astype(int)
df['o_far']=((df.dep_type=='other')&(df.ttd<=-4)).astype(int); df['o_mid']=((df.dep_type=='other')&(df.ttd.isin([-3,-2]))).astype(int); df['o_near']=((df.dep_type=='other')&(df.ttd>=-1)).astype(int)
# linear: ttd winsorized at -8, centered so that main effect = departure-year level
df['ttd_w'] = df.ttd.clip(lower=-8)
df['other_dep'] = (df.dep_type=='other').astype(int)
df['c_x_ttd'] = df.conf_cio*df.ttd_w; df['o_x_ttd'] = df.other_dep*df.ttd_w
# tenure halves for departing spells (observed departure), tot tenure = max cio_tenure in spell
dep = df.departs_obs==1
df['tot_ten'] = df[dep].groupby('spell').cio_tenure.transform('max')
df['second_half'] = np.where(dep & df.tot_ten.notna(), (df.cio_tenure > df.tot_ten/2).astype(float), np.nan)
df['second_half_ge'] = np.where(dep & df.tot_ten.notna(), (df.cio_tenure >= df.tot_ten/2).astype(float), np.nan)
df['c_second'] = df.conf_cio*df.second_half; df['o_second'] = df.other_dep*df.second_half
df['c_second_ge'] = df.conf_cio*df.second_half_ge; df['o_second_ge'] = df.other_dep*df.second_half_ge

CTRL = 'size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB + sib1 + cio_age + cio_tenure + prior_private_exp + Elite_inst'
CTRL_SPELL = 'size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB'   # age/tenure/sib/priv/elite absorbed or collinear within spell

def fit(y, rhs, fe='ppd_id + fy', data=None):
    d = df if data is None else data
    return pf.feols(f'{y} ~ {rhs} | {fe}', data=d, vcov={'CRV1':'ppd_id'})

def lincom(m, w):
    """linear combination w (dict name->weight) of coefficients: est, se, p (t with G-1 df)"""
    names = list(m._coefnames); b = np.asarray(m._beta_hat); V = np.asarray(m._vcov)
    c = np.zeros(len(names))
    for k,v in w.items():
        if k not in names: return (np.nan, np.nan, np.nan)
        c[names.index(k)] = v
    est = c@b; se = np.sqrt(c@V@c); G = m._G[0] if hasattr(m,'_G') else 150
    p = 2*stats.t.sf(abs(est/se), df=G-1)
    return est, se, p

def wald(m, rows):
    """joint test that each linear combination in rows (list of dicts) = 0; F with (k, G-1)"""
    names = list(m._coefnames); b = np.asarray(m._beta_hat); V = np.asarray(m._vcov)
    R = np.zeros((len(rows), len(names)))
    for i,w in enumerate(rows):
        for k,v in w.items():
            if k not in names: return (np.nan, np.nan)
            R[i, names.index(k)] = v
    Rb = R@b; RVR = R@V@R.T
    W = Rb@np.linalg.solve(RVR, Rb); k = len(rows); G = m._G[0]
    F = W/k; p = stats.f.sf(F, k, G-1)
    return F, p

def star(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fmt(est,se,p):
    if np.isnan(est): return "   (not identified)"
    return f"{est:7.3f}{star(p):3s} ({se:.3f}) p={p:.3f}"

out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

P("# Time-to-departure / dose-response analysis")
P(f"Sample: {len(df)} plan-years, {df.ppd_id.nunique()} plans, {df.spell.nunique()} CIO-plan spells. Returns in percentage points.")
P("Baseline controls:", CTRL, "| plan FE + year FE, SE clustered by plan.\n")

P("## 0. Counts by departure type and years-to-departure bin")
P(pd.crosstab(df.dep_type, df['bin']).reindex(columns=BINS+['na']).to_string()); P("")
P("Raw mean peer-adjusted return (pp) by bin:")
P(df[df.dep_type.isin(['conf','other'])].groupby(['dep_type','bin']).ret100.agg(['mean','count']).unstack(0).round(3).reindex(BINS).to_string()); P("")
P("Raw mean total fee pct (pp of assets) by bin:")
P(df[df.dep_type.isin(['conf','other'])].groupby(['dep_type','bin']).fee100.agg(['mean','count']).unstack(0).round(3).reindex(BINS).to_string()); P("")

# ---------- 1. baseline
P("## 1. Baseline (reconstructed Table III spec)")
for y in ['ret100','bret100']:
    m = fit(y, f'conf_cio + {CTRL}')
    P(f"{y}: Conflicted = {fmt(m.coef()['conf_cio'], m.se()['conf_cio'], m.pvalue()['conf_cio'])}  N={m._N}")
P("")

# ---------- 2. bins
def bins_block(y, fe, ctrl, label, data=None, rel=False):
    """rel=True: omit the <=-5 bin so each coefficient is relative to the CIO's own far-from-departure years (needed with spell FE)."""
    use = BINS[1:] if rel else BINS
    cb = ' + '.join([f'c_{b}' for b in use]); ob = ' + '.join([f'o_{b}' for b in use])
    m = fit(y, f'{cb} + {ob} + {ctrl}', fe=fe, data=data)
    P(f"### {label}: y={y}, FE={fe}, N={m._N}" + ("  [coefficients relative to own <=-5 bin]" if rel else ""))
    P(f"{'bin':6s} {'Conflicted x bin':34s} {'Other-departure x bin':34s} {'Difference (conf - other)':34s}")
    for b in use:
        c = lincom(m,{f'c_{b}':1}); o = lincom(m,{f'o_{b}':1}); d = lincom(m,{f'c_{b}':1,f'o_{b}':-1})
        P(f"{b:6s} {fmt(*c):34s} {fmt(*o):34s} {fmt(*d):34s}")
    if rel:
        F,p = wald(m, [{f'c_{b}':1} for b in use]);  P(f"  Flatness test, conflicted bins all = far bin:        F={F:.2f} p={p:.3f}")
        F,p = wald(m, [{f'o_{b}':1} for b in use]);  P(f"  Flatness test, other-departure bins all = far bin:   F={F:.2f} p={p:.3f}")
        F,p = wald(m, [{f'c_{b}':1, f'o_{b}':-1} for b in use]); P(f"  Joint test conf profile == other profile:            F={F:.2f} p={p:.3f}")
        nf_c = lincom(m, {'c_m2':1/3,'c_m1':1/3,'c_p0':1/3,'c_m4':-.5}); nf_o = lincom(m, {'o_m2':1/3,'o_m1':1/3,'o_p0':1/3,'o_m4':-.5})
        dd = lincom(m, {'c_m2':1/3,'c_m1':1/3,'c_p0':1/3,'c_m4':-.5,'o_m2':-1/3,'o_m1':-1/3,'o_p0':-1/3,'o_m4':.5})
        nf_c5 = lincom(m, {'c_m2':1/3,'c_m1':1/3,'c_p0':1/3}); nf_o5 = lincom(m, {'o_m2':1/3,'o_m1':1/3,'o_p0':1/3}); dd5 = lincom(m, {'c_m2':1/3,'c_m1':1/3,'c_p0':1/3,'o_m2':-1/3,'o_m1':-1/3,'o_p0':-1/3})
        P(f"  Near(-2..0) minus <=-5 bin, conflicted:              {fmt(*nf_c5)}   other: {fmt(*nf_o5)}   DiD: {fmt(*dd5)}")
        P(f"  Near(-2..0) minus Far(-4 & <=-5 avg), conflicted:    {fmt(*nf_c)}   other: {fmt(*nf_o)}   DiD: {fmt(*dd)}")
        P("")
        return m
    F,p = wald(m, [{f'c_{BINS[i]}':1, f'c_{BINS[i+1]}':-1} for i in range(len(BINS)-1)])
    P(f"  Flatness test, conflicted bins all equal:            F={F:.2f} p={p:.3f}")
    F,p = wald(m, [{f'o_{BINS[i]}':1, f'o_{BINS[i+1]}':-1} for i in range(len(BINS)-1)])
    P(f"  Flatness test, other-departure bins all equal:       F={F:.2f} p={p:.3f}")
    F,p = wald(m, [{f'c_{b}':1, f'o_{b}':-1} for b in BINS])
    P(f"  Joint test conf profile == other profile (all bins): F={F:.2f} p={p:.3f}")
    near = {'c_m2':1/3,'c_m1':1/3,'c_p0':1/3}; far = {'c_m5':.5,'c_m4':.5}
    nf_c = lincom(m, {**near, **{k:-v for k,v in far.items()}})
    nf_o = lincom(m, {'o_m2':1/3,'o_m1':1/3,'o_p0':1/3,'o_m5':-.5,'o_m4':-.5})
    dd = lincom(m, {**{k:v for k,v in near.items()}, **{k:-v for k,v in far.items()}, 'o_m2':-1/3,'o_m1':-1/3,'o_p0':-1/3,'o_m5':.5,'o_m4':.5})
    P(f"  Near(-2..0) minus Far(<=-4), conflicted:             {fmt(*nf_c)}")
    P(f"  Near minus Far, other departures:                    {fmt(*nf_o)}")
    P(f"  Diff-in-diff (conf near-far) - (other near-far):     {fmt(*dd)}")
    near2 = {'c_m2':.5,'c_m1':.5}
    nf_c2 = lincom(m, {**near2, 'c_m5':-.5,'c_m4':-.5}); dd2 = lincom(m, {**near2,'c_m5':-.5,'c_m4':-.5,'o_m2':-.5,'o_m1':-.5,'o_m5':.5,'o_m4':.5})
    P(f"  Near(-2,-1) minus Far, conflicted (excl. dep. year): {fmt(*nf_c2)}   DiD: {fmt(*dd2)}")
    P("")
    return m

P("## 2. Years-to-departure bins (reference: CIO-years with no observed departure)")
for y in ['ret100','bret100']:
    bins_block(y, 'ppd_id + fy', CTRL, 'Pooled, plan+year FE')
for y in ['ret100','bret100']:
    bins_block(y, 'spell + fy', CTRL_SPELL, 'Within CIO-spell FE (profile identified within CIO)', rel=True)

# ---------- 3. coarse 3-bin version
P("## 3. Coarse bins: far (<=-4) / mid (-3,-2) / near (-1,0)")
for y in ['ret100','bret100']:
    for fe,ctrl in [('ppd_id + fy',CTRL),('spell + fy',CTRL_SPELL)]:
        rhs = f'c_far + c_mid + c_near + o_far + o_mid + o_near + {ctrl}' if fe.startswith('ppd') else f'c_mid + c_near + o_mid + o_near + {ctrl}'
        m = fit(y, rhs, fe=fe)
        P(f"y={y} FE={fe} N={m._N}" + ("  [relative to own far years]" if fe.startswith('spell') else ""))
        for b in (['far','mid','near'] if fe.startswith('ppd') else ['mid','near']):
            P(f"  {b:5s} conf {fmt(*lincom(m,{f'c_{b}':1})):34s} other {fmt(*lincom(m,{f'o_{b}':1})):34s} diff {fmt(*lincom(m,{f'c_{b}':1,f'o_{b}':-1}))}")
        if fe.startswith('ppd'):
            P(f"  conf near-far {fmt(*lincom(m,{'c_near':1,'c_far':-1}))} | other near-far {fmt(*lincom(m,{'o_near':1,'o_far':-1}))} | DiD {fmt(*lincom(m,{'c_near':1,'c_far':-1,'o_near':-1,'o_far':1}))}")
        else:
            P(f"  conf near-far {fmt(*lincom(m,{'c_near':1}))} | other near-far {fmt(*lincom(m,{'o_near':1}))} | DiD {fmt(*lincom(m,{'c_near':1,'o_near':-1}))}")
P("")

# ---------- 4. linear slope
P("## 4. Linear dose-response: y ~ Conf + Conf x YearsToDeparture + Other + Other x YearsToDeparture (ttd winsorized at -8; slope = change per year closer to exit)")
for y in ['ret100','bret100','fee100','expr100']:
    for fe,ctrl in [('ppd_id + fy',CTRL),('spell + fy',CTRL_SPELL)]:
        rhs = f'conf_cio + c_x_ttd + other_dep + o_x_ttd + {ctrl}' if fe.startswith('ppd') else f'c_x_ttd + o_x_ttd + {ctrl}'
        m = fit(y, rhs, fe=fe)
        sc = lincom(m,{'c_x_ttd':1}); so = lincom(m,{'o_x_ttd':1}); dd = lincom(m,{'c_x_ttd':1,'o_x_ttd':-1})
        lvl = f"  Conf level at exit yr {fmt(*lincom(m,{'conf_cio':1}))}" if fe.startswith('ppd') else ''
        P(f"y={y:8s} FE={fe:12s} N={m._N}: slope conf {fmt(*sc)} | slope other {fmt(*so)} | diff {fmt(*dd)}{lvl}")
P("")

# ---------- 5. tenure halves
P("## 5. First vs second half of tenure (departing spells only; second half = tenure > final tenure / 2)")
sub = df[df.second_half.notna()]
P("Counts:"); P(pd.crosstab(sub.dep_type, sub.second_half).to_string())
for y in ['ret100','bret100','fee100','expr100']:
    for fe,ctrl in [('ppd_id + fy',CTRL),('spell + fy',CTRL_SPELL)]:
        rhs = f'conf_cio + c_second + o_second + {ctrl}' if fe.startswith('ppd') else f'c_second + o_second + {ctrl}'
        m = fit(y, rhs, fe=fe, data=sub)
        a = lincom(m,{'c_second':1}); b = lincom(m,{'o_second':1}); d = lincom(m,{'c_second':1,'o_second':-1})
        lvl = f" | conf 1st-half level {fmt(*lincom(m,{'conf_cio':1}))}" if fe.startswith('ppd') else ''
        P(f"y={y:8s} FE={fe:12s} N={m._N}: 2nd-half effect conf {fmt(*a)} | other {fmt(*b)} | diff {fmt(*d)}{lvl}")
P("  (robustness: second half defined with >=)")
for y in ['ret100','bret100']:
    m = fit(y, f'conf_cio + c_second_ge + o_second_ge + {CTRL}', data=sub)
    P(f"y={y:8s} pooled N={m._N}: conf {fmt(*lincom(m,{'c_second_ge':1}))} | other {fmt(*lincom(m,{'o_second_ge':1}))} | diff {fmt(*lincom(m,{'c_second_ge':1,'o_second_ge':-1}))}")
P("")

# ---------- 6. fees & allocation by bins
P("## 6. Fee and allocation profiles by years-to-departure bin (pooled plan+year FE, baseline controls)")
for y in ['fee100','expr100','pefee100','refee100','hffee100','eqfee100','fifee100','total_fee_rank','alt_actl','PETotal_Actl']:
    bins_block(y, 'ppd_id + fy', CTRL, 'Pooled')
P("## 6b. Fee profiles within CIO-spell")
for y in ['fee100','expr100','pefee100','alt_actl']:
    bins_block(y, 'spell + fy', CTRL_SPELL, 'Within spell', rel=True)

# ---------- 6c. robustness of the returns profile
P("## 6c. Robustness of the returns profile (coarse bins, pooled)")
df['ten_bin'] = pd.cut(df.cio_tenure, [-1,0,1,2,3,4,6,9,100], labels=False)
for y in ['ret100','bret100']:
    m = fit(y, f'c_far + c_mid + c_near + o_far + o_mid + o_near + {CTRL} + C(ten_bin)')
    P(f"(a) tenure bins instead of linear tenure, y={y} N={m._N}: conf far {fmt(*lincom(m,{'c_far':1}))} near {fmt(*lincom(m,{'c_near':1}))} near-far {fmt(*lincom(m,{'c_near':1,'c_far':-1}))} | DiD {fmt(*lincom(m,{'c_near':1,'c_far':-1,'o_near':-1,'o_far':1}))}")
    d2 = df[df.dep_type!='unknown']
    m = fit(y, f'c_far + c_mid + c_near + o_far + o_mid + o_near + {CTRL}', data=d2)
    P(f"(b) drop unknown-exit spells, y={y} N={m._N}: conf far {fmt(*lincom(m,{'c_far':1}))} near {fmt(*lincom(m,{'c_near':1}))} near-far {fmt(*lincom(m,{'c_near':1,'c_far':-1}))} | DiD {fmt(*lincom(m,{'c_near':1,'c_far':-1,'o_near':-1,'o_far':1}))}")
    d3 = df[df.dep_type.isin(['conf','other'])]
    m = fit(y, f'c_far + c_mid + c_near + o_mid + o_near + {CTRL}', data=d3)
    P(f"(c) departing spells only (ref = other far), y={y} N={m._N}: conf far {fmt(*lincom(m,{'c_far':1}))} near {fmt(*lincom(m,{'c_near':1}))} near-far {fmt(*lincom(m,{'c_near':1,'c_far':-1}))} | DiD {fmt(*lincom(m,{'c_near':1,'c_far':-1,'o_near':-1}))}")
    m = fit(y, f'c_far + c_mid + c_near + o_far + o_mid + o_near + {CTRL}', fe='ppd_id + fy', data=df[df.conf_cio.eq(0) | df.cio_tenure.le(12)])
    d4 = df[(df.dep_type!='conf') | (df.tot_ten.fillna(99)>=4)]
    m = fit(y, f'c_far + c_mid + c_near + o_far + o_mid + o_near + {CTRL}', data=d4)
    P(f"(d) conflicted spells with final tenure >= 4 only (same CIOs in far & near), y={y} N={m._N}: conf far {fmt(*lincom(m,{'c_far':1}))} near {fmt(*lincom(m,{'c_near':1}))} near-far {fmt(*lincom(m,{'c_near':1,'c_far':-1}))} | DiD {fmt(*lincom(m,{'c_near':1,'c_far':-1,'o_near':-1,'o_far':1}))}")
P("")
P("## 6d. Authors' own close_conf / far_conf split, for reference")
for y in ['ret100','bret100','fee100','expr100']:
    m = fit(y, f'close_conf + far_conf + {CTRL}')
    P(f"y={y:8s} N={m._N}: close {fmt(*lincom(m,{'close_conf':1}))} | far {fmt(*lincom(m,{'far_conf':1}))} | close-far {fmt(*lincom(m,{'close_conf':1,'far_conf':-1}))}")
P("")

# ---------- 7. mediation
P("## 7. Mediation: does controlling for fees absorb the conflicted / near-departure effect?")
for y in ['ret100','bret100']:
    s = df[df.fee100.notna()]
    m0 = fit(y, f'conf_cio + {CTRL}', data=s); m1 = fit(y, f'conf_cio + fee100 + {CTRL}', data=s); m2 = fit(y, f'conf_cio + slope_fee_pct_controls + {CTRL}', data=s[s.slope_fee_pct_controls.notna()])
    P(f"y={y}: same sample N={m0._N}: Conf no fee ctrl {fmt(m0.coef()['conf_cio'],m0.se()['conf_cio'],m0.pvalue()['conf_cio'])} | with fee level {fmt(m1.coef()['conf_cio'],m1.se()['conf_cio'],m1.pvalue()['conf_cio'])} (fee coef {fmt(m1.coef()['fee100'],m1.se()['fee100'],m1.pvalue()['fee100'])}) | with authors' Fee Slope var (N={m2._N}) {fmt(m2.coef()['conf_cio'],m2.se()['conf_cio'],m2.pvalue()['conf_cio'])}")
    m0 = fit(y, f'c_far + c_mid + c_near + o_far + o_mid + o_near + {CTRL}', data=s); m1 = fit(y, f'c_far + c_mid + c_near + o_far + o_mid + o_near + fee100 + {CTRL}', data=s)
    P(f"   near-departure conf effect: no fee ctrl {fmt(*lincom(m0,{'c_near':1}))} | with fee ctrl {fmt(*lincom(m1,{'c_near':1}))}")
P("")

# ---------- 8. placebo departure types' profiles
P("## 8. Near-minus-far profile by departure type (pooled plan+year FE). Types among non-conflicted observed departures.")
df['typ'] = np.select([df.dep_type=='conf', (df.dep_type=='other')&(df.ever_retire==1), (df.dep_type=='other')&(df.ever_leave_pub==1), (df.dep_type=='other')&(df.priv_nonam_job==1)],
                      ['conf','retire','public','privnonam'], default='none')
P(pd.crosstab(df.typ, df['bin']).reindex(columns=BINS+['na']).to_string())
terms=[]
for t in ['conf','retire','public','privnonam']:
    for b in ['far','mid','near']:
        cond = {'far':df.ttd<=-4,'mid':df.ttd.isin([-3,-2]),'near':df.ttd>=-1}[b]
        df[f'{t}_{b}'] = ((df.typ==t)&cond).astype(int); terms.append(f'{t}_{b}')
for y in ['ret100','bret100','fee100']:
    m = fit(y, ' + '.join(terms)+' + '+CTRL)
    P(f"y={y} N={m._N}")
    for t in ['conf','retire','public','privnonam']:
        nf = lincom(m,{f'{t}_near':1,f'{t}_far':-1})
        dd = lincom(m,{'conf_near':1,'conf_far':-1,f'{t}_near':-1,f'{t}_far':1}) if t!='conf' else (np.nan,np.nan,np.nan)
        P(f"  {t:10s} far {fmt(*lincom(m,{f'{t}_far':1})):30s} near {fmt(*lincom(m,{f'{t}_near':1})):30s} near-far {fmt(*nf):30s}" + (f" conf minus this type {fmt(*dd)}" if t!='conf' else ''))
P("")
open(os.path.join(OUT,'results_full.md'),'w').write('\n'.join(out))
df.to_pickle(os.path.join(OUT,'df_built.pkl'))
