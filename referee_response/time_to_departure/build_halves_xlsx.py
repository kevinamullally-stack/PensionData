import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_built.pkl')).sort_values(['spell','fy']).copy()
CTRL = ['size','ActFundedRatio_GASB','InvestmentReturnAssumption_GASB','sib1','cio_age','cio_tenure','prior_private_exp','Elite_inst']
CS = ['size','ActFundedRatio_GASB','InvestmentReturnAssumption_GASB']
dep = df.departs_obs==1; g = df[dep].groupby('spell')
df['ten_dep'] = np.nan
df.loc[dep,'ten_dep'] = g.cio_tenure.transform('max') + (g.year_departs.transform('max') - g.fy.transform('max')).clip(lower=0)
df['second'] = np.where(dep & df.ten_dep.notna() & (df.ten_dep>0), (df.cio_tenure > df.ten_dep/2).astype(float), np.nan)
df['frac'] = np.where(dep & (df.ten_dep>0), df.cio_tenure/df.ten_dep, np.nan)
df['last2'] = np.where(dep, (df.ttd>=-1).astype(float), np.nan)
df['other_dep'] = (df.dep_type=='other').astype(int)
for v in ['second','frac','last2']:
    df[f'c_{v}'] = df.conf_cio*df[v]; df[f'o_{v}'] = df.other_dep*df[v]
S = df[df.second.notna() & df.dep_type.isin(['conf','other'])].copy()
LAB = {'conf_cio':'Conflicted CIO (first-half level vs. other departers)','c_second':'Conflicted x Second half of tenure','o_second':'Other departure x Second half of tenure',
       'c_frac':'Conflicted x Fraction of tenure elapsed','o_frac':'Other departure x Fraction of tenure elapsed','c_last2':'Conflicted x Last two years','o_last2':'Other departure x Last two years',
       'size':'Log plan size','ActFundedRatio_GASB':'Funded ratio (GASB)','InvestmentReturnAssumption_GASB':'Return assumption','sib1':'Separate investment board',
       'cio_age':'CIO age','cio_tenure':'CIO tenure (years)','prior_private_exp':'Prior private-sector experience','Elite_inst':'Elite institution'}
CLUSTERS = [('cio','CIO'),('ppd_id','Plan'),('system_id','System')]
def fit(y, rhs, fe, d, cl): return pf.feols(f'{y} ~ {" + ".join(rhs)} | {fe}', data=d, vcov={'CRV1':cl})
def lin(m, w):
    names=list(m._coefnames); b=np.asarray(m._beta_hat); V=np.asarray(m._vcov); c=np.zeros(len(names))
    for k,v in w.items(): c[names.index(k)]=v
    return float(c@b), float(np.sqrt(c@V@c))

def spec_table(y, rhs, fe, d, diff_key=('c_second','o_second')):
    ms = {cl: fit(y, rhs, fe, d, cl) for cl,_ in CLUSTERS}
    m = ms['cio']; names = list(m._coefnames)
    rows = []
    for n in names:
        r = {'var': LAB.get(n,n), 'coef': float(m.coef()[n])}
        for cl,_ in CLUSTERS: r[f'se_{cl}'] = float(ms[cl].se()[n])
        rows.append(r)
    dr = {'var': f'Difference: {LAB[diff_key[0]]} minus {LAB[diff_key[1]]}'}
    for cl,_ in CLUSTERS:
        e, se = lin(ms[cl], {diff_key[0]:1, diff_key[1]:-1}); dr['coef']=e; dr[f'se_{cl}']=se
    rows.append(dr)
    meta = {'N': int(m._N), 'G': {cl:int(ms[cl]._G[0]) for cl,_ in CLUSTERS}, 'r2': float(m._r2), 'r2w': float(m._r2_within) if m._r2_within is not None else None,
            'n_conf_cio': int(d[d.conf_cio==1].cio.nunique()), 'n_conf_rows': int((d.conf_cio==1).sum()), 'n_other_cio': int(d[d.other_dep==1].cio.nunique())}
    return rows, meta

YL = {'ret100':'Peer-adjusted return (pp)','bret100':'Benchmark-adjusted return (pp)'}
SPECS = []
for y in ['ret100','bret100']:
    SPECS.append(dict(title=f'{YL[y]} | Pooled | Plan + fiscal-year FE', y=y, rhs=['conf_cio','c_second','o_second']+CTRL, fe='ppd_id + fy', d=S, fe_text='Plan FE, fiscal-year FE', key=('c_second','o_second')))
    SPECS.append(dict(title=f'{YL[y]} | Within CIO | CIO-spell + fiscal-year FE', y=y, rhs=['c_second','o_second']+CS, fe='spell + fy', d=S, fe_text='CIO-plan spell FE, fiscal-year FE (CIO-level controls absorbed)', key=('c_second','o_second')))
ROB = []
S4 = S[S.ten_dep>=4]
for y in ['ret100','bret100']:
    ROB.append(dict(title=f'{YL[y]} | Within CIO | Tenure at departure >= 4 years only', y=y, rhs=['c_second','o_second']+CS, fe='spell + fy', d=S4, fe_text='CIO-plan spell FE, fiscal-year FE; CIOs with final tenure >= 4', key=('c_second','o_second')))
    ROB.append(dict(title=f'{YL[y]} | Within CIO | Last two years vs. earlier', y=y, rhs=['c_last2','o_last2']+CS, fe='spell + fy', d=S, fe_text='CIO-plan spell FE, fiscal-year FE', key=('c_last2','o_last2')))
    ROB.append(dict(title=f'{YL[y]} | Within CIO | Fraction of tenure elapsed (continuous, 0 to 1)', y=y, rhs=['c_frac','o_frac']+CS, fe='spell + fy', d=S[S.frac.notna()], fe_text='CIO-plan spell FE, fiscal-year FE', key=('c_frac','o_frac')))
    ROB.append(dict(title=f'{YL[y]} | Pooled | Fraction of tenure elapsed (continuous, 0 to 1)', y=y, rhs=['conf_cio','c_frac','o_frac']+CTRL, fe='ppd_id + fy', d=S[S.frac.notna()], fe_text='Plan FE, fiscal-year FE', key=('c_frac','o_frac')))

# person-level paired tests
P = S.groupby(['cio','conf_cio','fy','second'], as_index=False)[['ret100','bret100']].mean()
paired = []
for y in ['ret100','bret100']:
    H = P.groupby(['cio','conf_cio','second'])[y].mean().unstack('second').dropna(); H['chg']=H[1.0]-H[0.0]
    for grp,lab in [(1,'Conflicted CIOs'),(0,'Other departing CIOs')]:
        x = H.xs(grp, level='conf_cio').chg
        paired.append(dict(y=YL[y], group=lab, n=len(x), mean_first=float(H.xs(grp,level='conf_cio')[0.0].mean()), mean_second=float(H.xs(grp,level='conf_cio')[1.0].mean()),
            mean_chg=float(x.mean()), sd_chg=float(x.std()), median_chg=float(x.median()), share_up=float((x>0).mean()),
            p_t=float(stats.ttest_1samp(x,0).pvalue), p_wilcoxon=float(stats.wilcoxon(x).pvalue), p_sign=float(stats.binomtest(int((x>0).sum()), len(x)).pvalue)))
    xc = H.xs(1,level='conf_cio').chg; xo = H.xs(0,level='conf_cio').chg
    paired.append(dict(y=YL[y], group='Conflicted minus other (two-sample)', n=len(xc)+len(xo), mean_first=np.nan, mean_second=np.nan, mean_chg=float(xc.mean()-xo.mean()), sd_chg=np.nan, median_chg=float(xc.median()-xo.median()), share_up=np.nan,
        p_t=float(stats.ttest_ind(xc,xo,equal_var=False).pvalue), p_wilcoxon=float(stats.mannwhitneyu(xc,xo).pvalue), p_sign=np.nan))

# ---------------- workbook
wb = Workbook(); F='Arial'
H1=Font(name=F,size=12,bold=True); HB=Font(name=F,size=10,bold=True); N=Font(name=F,size=10); BLUE=Font(name=F,size=10,color='0000FF'); IT=Font(name=F,size=9,italic=True,color='555555')
FILL=PatternFill('solid',fgColor='DDEBF7'); thin=Side(style='thin',color='BBBBBB'); BOT=Border(bottom=thin)
def setw(ws, widths):
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width = w

# Notes sheet
ws = wb.active; ws.title='Notes'
notes = [
 ('First half vs. second half of CIO tenure: regression results for conflicted CIOs', H1),
 ('Prepared for the Financial Management revision of "Conflicted CIOs" (Referee Major Concern 3). Source data: data_v3_3.dta. Code: halves_analysis.py in referee_response/time_to_departure.', N),
 ('', N),
 ('Sample', HB),
 ('CIO-plan-years of CIOs with an observed departure (conflicted CIOs and CIOs departing for any other reason). CIOs still in office in 2020 and CIOs who left for an unknown destination are excluded, because tenure halves are undefined for them.', N),
 ('Tenure at departure = CIO tenure in the last observed fiscal year plus any gap between that year and the departure year. Second half = CIO tenure > tenure at departure / 2. First half is the omitted category.', N),
 ('Conflicted CIO = baseline definition (conf_cio): CIO who eventually departs for an investment vendor. Other departure = retirement, move to another public plan, move to a non-vendor private job, dismissal, or death.', N),
 ('Returns are in percentage points. Peer-adjusted = plan return minus peer-group return; benchmark-adjusted = plan return minus the plan\'s own policy benchmark.', N),
 ('', N),
 ('How to read the tables', HB),
 ('"Conflicted x Second half" is the change in a conflicted CIO\'s performance from the first half to the second half of tenure. "Other departure x Second half" is the same change for other departing CIOs. "Difference" is the conflict-specific component (first minus second).', N),
 ('In the pooled specifications "Conflicted CIO" is the first-half level of conflicted CIOs relative to the first half of other departing CIOs. In the within-CIO specifications that level is absorbed by the CIO-spell fixed effects.', N),
 ('Blue cells are estimates pasted from the regression output (coefficients, standard errors, sample sizes, cluster counts). t-statistics, p-values, confidence intervals and significance stars are spreadsheet formulas based on those cells, using the t distribution with (clusters - 1) degrees of freedom.', N),
 ('Three standard errors are shown for every coefficient: clustered by CIO (preferred, since one CIO can run several plans in one system), by plan (the paper\'s convention), and by system.', N),
 ('Significance stars: *** p<0.01, ** p<0.05, * p<0.10, using the CIO-clustered standard error.', N),
 ('', N),
 ('Sheets', HB),
 ('Summary: one row per specification with the three key coefficients. Main: full coefficient tables for the four main specifications. Robustness: tenure >= 4, last two years, fraction of tenure elapsed. Paired: person-level paired tests, one observation per CIO.', N),
]
for i,(t,f) in enumerate(notes,1):
    c=ws.cell(row=i,column=1,value=t); c.font=f; c.alignment=Alignment(wrap_text=True,vertical='top')
setw(ws,[140])

# full-table writer
def write_spec(ws, r0, sp, rows, meta):
    ws.cell(row=r0,column=1,value=sp['title']).font=H1
    ws.cell(row=r0+1,column=1,value=f"Fixed effects: {sp['fe_text']}. Dependent variable: {YL[sp['y']]}.").font=IT
    hdr = ['Variable','Coefficient','SE (CIO)','t (CIO)','p (CIO)','Sig.','95% CI low (CIO)','95% CI high (CIO)','SE (Plan)','p (Plan)','SE (System)','p (System)']
    for j,h in enumerate(hdr,1):
        c=ws.cell(row=r0+2,column=j,value=h); c.font=HB; c.fill=FILL; c.alignment=Alignment(horizontal='center',wrap_text=True); c.border=BOT
    # meta block to the right: N, clusters, R2, critical t
    mr = r0+2; mc = 14
    labels = [('Observations',meta['N']),('Clusters (CIO)',meta['G']['cio']),('Clusters (Plan)',meta['G']['ppd_id']),('Clusters (System)',meta['G']['system_id']),
              ('R-squared',round(meta['r2'],4)),('Within R-squared',None if meta['r2w'] is None else round(meta['r2w'],4)),
              ('Distinct conflicted CIOs',meta['n_conf_cio']),('Conflicted CIO-years',meta['n_conf_rows']),('Distinct other departing CIOs',meta['n_other_cio'])]
    for k,(l,v) in enumerate(labels):
        ws.cell(row=mr+k,column=mc,value=l).font=N; c=ws.cell(row=mr+k,column=mc+1,value=v); c.font=BLUE
    gcio=f"${get_column_letter(mc+1)}${mr+1}"; gpl=f"${get_column_letter(mc+1)}${mr+2}"; gsy=f"${get_column_letter(mc+1)}${mr+3}"
    ws.cell(row=mr+9,column=mc,value='Critical t, 95% (CIO clusters)').font=N; ws.cell(row=mr+9,column=mc+1,value=f"=TINV(0.05,{gcio}-1)").font=N
    tcrit=f"${get_column_letter(mc+1)}${mr+9}"
    r=r0+3
    for row in rows:
        is_diff = row['var'].startswith('Difference')
        ws.cell(row=r,column=1,value=row['var']).font=HB if is_diff else N
        ws.cell(row=r,column=2,value=round(row['coef'],4)).font=BLUE
        ws.cell(row=r,column=3,value=round(row['se_cio'],4)).font=BLUE
        ws.cell(row=r,column=4,value=f"=B{r}/C{r}").font=N
        ws.cell(row=r,column=5,value=f"=TDIST(ABS(D{r}),{gcio}-1,2)").font=N
        ws.cell(row=r,column=6,value=f'=IF(E{r}<0.01,"***",IF(E{r}<0.05,"**",IF(E{r}<0.1,"*","")))').font=N
        ws.cell(row=r,column=7,value=f"=B{r}-{tcrit}*C{r}").font=N
        ws.cell(row=r,column=8,value=f"=B{r}+{tcrit}*C{r}").font=N
        ws.cell(row=r,column=9,value=round(row['se_ppd_id'],4)).font=BLUE
        ws.cell(row=r,column=10,value=f"=TDIST(ABS(B{r}/I{r}),{gpl}-1,2)").font=N
        ws.cell(row=r,column=11,value=round(row['se_system_id'],4)).font=BLUE
        ws.cell(row=r,column=12,value=f"=TDIST(ABS(B{r}/K{r}),{gsy}-1,2)").font=N
        for j in [2,3,4,7,8,9,11]: ws.cell(row=r,column=j).number_format='0.000'
        for j in [5,10,12]: ws.cell(row=r,column=j).number_format='0.000'
        if is_diff:
            for j in range(1,13): ws.cell(row=r,column=j).border=Border(top=thin)
        r+=1
    return r+2

summary = []
for sheetname, speclist in [('Main',SPECS),('Robustness',ROB)]:
    ws = wb.create_sheet(sheetname); r=1
    for sp in speclist:
        rows, meta = spec_table(sp['y'], sp['rhs'], sp['fe'], sp['d'], sp['key'])
        start = r
        r = write_spec(ws, r, sp, rows, meta)
        # summary refs
        kc = [x for x in rows if x['var']==LAB[sp['key'][0]]][0]; ko = [x for x in rows if x['var']==LAB[sp['key'][1]]][0]; kd = rows[-1]
        lvl = [x for x in rows if x['var']==LAB['conf_cio']]
        summary.append(dict(sheet=sheetname, title=sp['title'], N=meta['N'], ncio=meta['n_conf_cio'], G=meta['G']['cio'],
            lvl=(lvl[0]['coef'], lvl[0]['se_cio']) if lvl else (None,None), c=(kc['coef'],kc['se_cio']), o=(ko['coef'],ko['se_cio']), d=(kd['coef'],kd['se_cio'])))
    setw(ws,[58,12,10,9,9,6,12,12,10,9,11,10,3,30,12])

# Summary sheet
ws = wb.create_sheet('Summary', 1)
ws.cell(row=1,column=1,value='Summary of first-half vs. second-half results (CIO-clustered standard errors; t-based p-values with clusters - 1 df)').font=H1
hdr=['Specification','N','Distinct conflicted CIOs','Clusters (CIO)','Conflicted first-half level','SE','p','Conflicted: 2nd half minus 1st half','SE','p','Other departures: 2nd half minus 1st half','SE','p','Difference (conflict-specific)','SE','p','95% CI low','95% CI high','Sig.']
for j,h in enumerate(hdr,1):
    c=ws.cell(row=3,column=j,value=h); c.font=HB; c.fill=FILL; c.alignment=Alignment(horizontal='center',wrap_text=True,vertical='center'); c.border=BOT
ws.row_dimensions[3].height=45
r=4
for s in summary:
    ws.cell(row=r,column=1,value=s['title']).font=N
    ws.cell(row=r,column=2,value=s['N']).font=BLUE; ws.cell(row=r,column=3,value=s['ncio']).font=BLUE; ws.cell(row=r,column=4,value=s['G']).font=BLUE
    if s['lvl'][0] is not None:
        ws.cell(row=r,column=5,value=round(s['lvl'][0],4)).font=BLUE; ws.cell(row=r,column=6,value=round(s['lvl'][1],4)).font=BLUE; ws.cell(row=r,column=7,value=f"=TDIST(ABS(E{r}/F{r}),$D{r}-1,2)").font=N
    else:
        ws.cell(row=r,column=5,value='absorbed').font=IT
    ws.cell(row=r,column=8,value=round(s['c'][0],4)).font=BLUE; ws.cell(row=r,column=9,value=round(s['c'][1],4)).font=BLUE; ws.cell(row=r,column=10,value=f"=TDIST(ABS(H{r}/I{r}),$D{r}-1,2)").font=N
    ws.cell(row=r,column=11,value=round(s['o'][0],4)).font=BLUE; ws.cell(row=r,column=12,value=round(s['o'][1],4)).font=BLUE; ws.cell(row=r,column=13,value=f"=TDIST(ABS(K{r}/L{r}),$D{r}-1,2)").font=N
    ws.cell(row=r,column=14,value=round(s['d'][0],4)).font=BLUE; ws.cell(row=r,column=15,value=round(s['d'][1],4)).font=BLUE; ws.cell(row=r,column=16,value=f"=TDIST(ABS(N{r}/O{r}),$D{r}-1,2)").font=N
    ws.cell(row=r,column=17,value=f"=N{r}-TINV(0.05,$D{r}-1)*O{r}").font=N; ws.cell(row=r,column=18,value=f"=N{r}+TINV(0.05,$D{r}-1)*O{r}").font=N
    ws.cell(row=r,column=19,value=f'=IF(P{r}<0.01,"***",IF(P{r}<0.05,"**",IF(P{r}<0.1,"*","")))').font=N
    for j in range(5,19): ws.cell(row=r,column=j).number_format='0.000'
    r+=1
ws.cell(row=r+1,column=1,value='Rows 4-7 are the main specifications (sheet Main); the remaining rows are robustness variants (sheet Robustness). For the fraction-of-tenure rows the coefficients are the change from the start to the end of tenure rather than a half-to-half change.').font=IT
setw(ws,[70,8,12,10,12,8,8,14,8,8,16,8,8,14,8,8,10,10,6])
ws.freeze_panes='B4'

# Paired sheet
ws = wb.create_sheet('Paired')
ws.cell(row=1,column=1,value='Person-level paired tests: each CIO\'s mean return in the second half of tenure minus the first half (plans averaged within CIO-year; one observation per CIO)').font=H1
hdr=['Outcome','Group','CIOs','Mean, first half','Mean, second half','Mean change','SD of change','Median change','Share improving','p: paired t / Welch t','p: Wilcoxon / Mann-Whitney','p: sign test']
for j,h in enumerate(hdr,1):
    c=ws.cell(row=3,column=j,value=h); c.font=HB; c.fill=FILL; c.alignment=Alignment(horizontal='center',wrap_text=True,vertical='center'); c.border=BOT
ws.row_dimensions[3].height=32
r=4
for p in paired:
    vals=[p['y'],p['group'],p['n'],p['mean_first'],p['mean_second'],p['mean_chg'],p['sd_chg'],p['median_chg'],p['share_up'],p['p_t'],p['p_wilcoxon'],p['p_sign']]
    for j,v in enumerate(vals,1):
        if isinstance(v,float) and np.isnan(v): v=None
        c=ws.cell(row=r,column=j,value=(round(v,4) if isinstance(v,float) else v)); c.font=BLUE if j>=3 else N
        if j>=4: c.number_format='0.000'
    r+=1
ws.cell(row=r+1,column=1,value='Means are in percentage points. The paired t, Wilcoxon signed-rank and sign tests are against a zero change for each group; the "Conflicted minus other" row uses Welch\'s t and Mann-Whitney on the two groups\' changes. Fewer CIOs appear here than in the regressions because the benchmark-adjusted series is missing for some plans and a CIO needs at least one year in each half.').font=IT
setw(ws,[30,34,8,12,12,12,12,12,12,14,16,12])

out='/home/user/PensionData/referee_response/time_to_departure/halves_regressions.xlsx'
wb.save(out); print('saved', out)
