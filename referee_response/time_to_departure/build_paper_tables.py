import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

df = pd.read_pickle(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'df_do.pkl')).sort_values(['spell','fy']).copy()
df['fee_ratio_pct'] = df.total_fee_pct*100
# paper sample and definition (do-file): cio_dum==1 & fy<=2020 & curr1==0 ; Conflicted = conf_pen_vendor
S0 = df[(df.cio_dum==1)&(df.fy<=2020)&(df.curr1==0)].copy()
S0['last_fy'] = S0.groupby('spell').fy.transform('max'); S0['max_ten'] = S0.groupby('spell').cio_tenure.transform('max')
S0['ydep'] = S0.year_departs; S0.loc[(S0.curr==0)&S0.ydep.isna(),'ydep'] = S0.last_fy
S0['ten_dep'] = S0.max_ten + (S0.ydep - S0.last_fy).clip(lower=0)
C = S0[(S0.conf_pen_vendor==1)&(S0.curr==0)&S0.ten_dep.notna()&(S0.ten_dep>0)&S0.cio_tenure.notna()].copy()
C['second'] = (C.cio_tenure > C.ten_dep/2).astype(float)
print("sample:", len(C), "CIO-years;", C.cio.nunique(), "CIOs;", C.spell.nunique(), "CIO-plan spells;", C.ppd_id.nunique(), "plans; second-half rows:", int(C.second.sum()), "; tenure>=4 CIOs:", C[C.ten_dep>=4].cio.nunique())

C1 = ['l_invret','size','l_fund']; C2 = ['l_eq','l_fi','l_re','l_pe','l_hf','l_alt','l_comd','l_cash']; C3=['fincenter1']; C4=['l_log_cio_age','l_log_cio_tenure','prior_private_exp','Elite_inst']; C5=['l_sib1','wstate_political']
LAB = {'second':'Second Half of Tenure (0/1)','l_invret':'Investment Return (t - 1)','size':'Log (Plan Size) (t-1)','l_fund':'Funding Ratio (t-1)',
 'l_eq':'Equity Allocation (%)','l_fi':'Fixed Income Allocation (%)','l_re':'Real Estate Allocation (%)','l_pe':'Private Equity Allocation (%)','l_hf':'Hedge Fund Allocation (%)',
 'l_alt':'Misc. Alternatives Allocation (%)','l_comd':'Commodities Allocation (%)','l_cash':'Cash Allocation (%)','fincenter1':'Financial Center (0/1)',
 'l_log_cio_age':'Log (CIO Age) (t-1)','l_log_cio_tenure':'Log (CIO Tenure) (t-1)','prior_private_exp':'CIO Prior Private Experience (0/1)','Elite_inst':'CIO Attended Elite College (0/1)',
 'l_sib1':'Separate Investment Board (0/1)','wstate_political':'% Political Appointees on Board'}
VARS = ['second']+C1+C2+C3+C4+C5
COLS = [dict(ctrl=C1+C2+C3, fe='fy', plan='No', year='Yes', ciofe='No', minten=''),
        dict(ctrl=C1+C2+C3+C4+C5, fe='fy', plan='No', year='Yes', ciofe='No', minten=''),
        dict(ctrl=C1+C2+C3+C4+C5, fe='ppd_id', plan='Yes', year='No', ciofe='No', minten=''),
        dict(ctrl=C1+C2+C3+C4+C5, fe='ppd_id + fy', plan='Yes', year='Yes', ciofe='No', minten=''),
        dict(ctrl=C1+C2+C3, fe='spell + fy', plan='No', year='Yes', ciofe='Yes', minten=''),
        dict(ctrl=C1+C2+C3, fe='spell + fy', plan='No', year='Yes', ciofe='Yes', minten='4')]
def run(y, col, d):
    dd = d if col['minten']=='' else d[d.ten_dep>=float(col['minten'])]
    m = pf.feols(f'{y} ~ second + {" + ".join(col["ctrl"])} | {col["fe"]}', data=dd, vcov={'CRV1':'ppd_id + fy'})
    used = dd.dropna(subset=[y,'second']+col['ctrl'])
    V = np.asarray(m._vcov); w,Q = np.linalg.eigh((V+V.T)/2); Vp = (Q*np.clip(w,0,None))@Q.T   # force PSD as reghdfe does
    se = {n: float(np.sqrt(max(Vp[i,i],0))) for i,n in enumerate(m._coefnames)}
    return dict(est={n:(float(m.coef()[n]), se[n]) for n in m._coefnames}, N=int(m._N), Gp=int(m._G[0]), Gy=int(m._G[1]), adjr2=float(m._adj_r2), ncio=int(used.cio.nunique()), col=col)
TABLES = {'T1A':[run('peer_adj_ret100',c,C) for c in COLS], 'T1B':[run('bench_adj_ret_pct',c,C) for c in COLS], 'T2A':[run('fee_ratio_pct',c,C) for c in COLS]}
P = C.groupby(['cio','fy','second'], as_index=False)[['peer_adj_ret100','bench_adj_ret_pct','fee_ratio_pct']].mean()
PR=[]
for y,lab in [('peer_adj_ret100','Peer-Adjusted Return (%)'),('bench_adj_ret_pct','Benchmark-Adjusted Return (%)'),('fee_ratio_pct','Fee Ratio (%)')]:
    H = P.groupby(['cio','second'])[y].mean().unstack('second').dropna(); ch = H[1.0]-H[0.0]
    PR.append(dict(lab=lab, n=len(ch), m1=float(H[0.0].mean()), m2=float(H[1.0].mean()), sd=float(ch.std()), pw=float(stats.wilcoxon(ch).pvalue), up=float((ch>0).mean())))

wb = Workbook(); TNR='Times New Roman'; SZ=10.5
F=Font(name=TNR,size=SZ); FB=Font(name=TNR,size=SZ,bold=True); FI=Font(name=TNR,size=SZ,italic=True); BLUE=Font(name=TNR,size=SZ,color='0000FF')
thin=Side(style='thin'); CENTER=Alignment(horizontal='center',vertical='center',wrap_text=True); RIGHT=Alignment(horizontal='right'); JUST=Alignment(horizontal='justify',wrap_text=True,vertical='top')
E = wb.active; E.title='Estimates'
E['A1']='Estimates behind the tables (blue = regression output; t and p are formulas). Standard errors double clustered by plan and year; p-values use the t distribution with min(plan clusters, year clusters) - 1 degrees of freedom.'; E['A1'].font=FI
E.column_dimensions['A'].width=34
META=['Observations','Plan clusters','Year clusters','Adjusted R-squared','Number of CIOs']
rv={v:4+i for i,v in enumerate(VARS)}; rm={m:4+len(VARS)+1+i for i,m in enumerate(META)}
E['A3']='Variable'; E['A3'].font=FB
for v in VARS: E.cell(row=rv[v],column=1,value=LAB[v]).font=F
for m in META: E.cell(row=rm[m],column=1,value=m).font=F
REF={}; k=0
for tab,regs in TABLES.items():
    for i,reg in enumerate(regs):
        c0=2+4*k; k+=1
        for j,h in enumerate(['coef','se','t','p']):
            cc=E.cell(row=3,column=c0+j,value=f'{tab}({i+1}) {h}'); cc.font=FB; cc.alignment=CENTER; E.column_dimensions[L(c0+j)].width=9
        dfree=f'MIN({L(c0)}{rm["Plan clusters"]},{L(c0)}{rm["Year clusters"]})-1'; refs={}
        for v in VARS:
            if v in reg['est']:
                b,se=reg['est'][v]; r=rv[v]
                E.cell(row=r,column=c0,value=b).font=BLUE; E.cell(row=r,column=c0+1,value=se).font=BLUE
                E.cell(row=r,column=c0+2,value=f'=IF({L(c0+1)}{r}>0,{L(c0)}{r}/{L(c0+1)}{r},"")').font=F
                E.cell(row=r,column=c0+3,value=f'=IF({L(c0+1)}{r}>0,TDIST(ABS({L(c0+2)}{r}),{dfree},2),"")').font=F
                for j in range(4): E.cell(row=r,column=c0+j).number_format='0.0000'
                refs[v]=dict(coef=f'Estimates!{L(c0)}{r}', t=f'Estimates!{L(c0+2)}{r}', p=f'Estimates!{L(c0+3)}{r}')
        for m,val in [('Observations',reg['N']),('Plan clusters',reg['Gp']),('Year clusters',reg['Gy']),('Adjusted R-squared',reg['adjr2']),('Number of CIOs',reg['ncio'])]:
            E.cell(row=rm[m],column=c0,value=val).font=BLUE; refs[m]=f'Estimates!{L(c0)}{rm[m]}'
        REF[(tab,i)]=refs
E.freeze_panes='B4'
def coef_f(ref): return f'=TEXT({ref["coef"]},"0.000")&IF({ref["p"]}="","",IF({ref["p"]}<0.01,"***",IF({ref["p"]}<0.05,"**",IF({ref["p"]}<0.1,"*",""))))'
def t_f(ref): return f'=IF({ref["t"]}="","(n/a)","("&TEXT({ref["t"]},"0.00")&")")'
def panel(ws, r, ptitle, deplab, tab, regs):
    n=len(regs); last=1+n
    if ptitle: ws.cell(row=r,column=1,value=ptitle).font=FB; r+=1
    for j in range(n): cc=ws.cell(row=r,column=2+j,value=f'({j+1})'); cc.font=F; cc.alignment=CENTER; cc.border=Border(top=thin)
    ws.cell(row=r,column=1).border=Border(top=thin); r+=1
    for j in range(n): cc=ws.cell(row=r,column=2+j,value=deplab); cc.font=F; cc.alignment=CENTER; cc.border=Border(bottom=thin)
    ws.cell(row=r,column=1).border=Border(bottom=thin); r+=1
    for v in VARS:
        if not any(v in REF[(tab,j)] for j in range(n)): continue
        ws.cell(row=r,column=1,value=LAB[v]).font=F
        for j in range(n):
            ref=REF[(tab,j)]
            if v in ref:
                cc=ws.cell(row=r,column=2+j,value=coef_f(ref[v])); cc.font=F; cc.alignment=RIGHT
                cc=ws.cell(row=r+1,column=2+j,value=t_f(ref[v])); cc.font=F; cc.alignment=RIGHT
        r+=2
    r+=1
    for lab,key,fmt in [('Observations','Observations','#,##0'),('Adjusted R-squared','Adjusted R-squared','0.000'),('Number of CIOs','Number of CIOs','0')]:
        ws.cell(row=r,column=1,value=lab).font=F
        for j in range(n): cc=ws.cell(row=r,column=2+j,value=f'={REF[(tab,j)][key]}'); cc.font=F; cc.alignment=RIGHT; cc.number_format=fmt
        r+=1
    for lab,key in [('Plan FE','plan'),('Year FE','year'),('CIO FE','ciofe'),('Min. Tenure at Departure (years)','minten')]:
        ws.cell(row=r,column=1,value=lab).font=F
        for j,reg in enumerate(regs): cc=ws.cell(row=r,column=2+j,value=reg['col'][key]); cc.font=F; cc.alignment=CENTER
        r+=1
    for c in range(1,last+1): ws.cell(row=r-1,column=c).border=Border(bottom=thin)
    return r+2
def table_sheet(name, title, notes, panels):
    ws=wb.create_sheet(name); ws.sheet_view.showGridLines=False; ws.column_dimensions['A'].width=34
    for c in range(2,8): ws.column_dimensions[L(c)].width=14
    ws.cell(row=1,column=1,value=title).font=FB
    ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=7); ws.cell(row=2,column=1,value=notes).font=F; ws.cell(row=2,column=1).alignment=JUST
    ws.row_dimensions[2].height=15*(len(notes)//105+2); r=4
    for ptitle,deplab,tab in panels: r=panel(ws,r,ptitle,deplab,tab,TABLES[tab])
notes1=("This table reports results of tests that regress the returns of public pension plans run by conflicted CIOs on an indicator variable, Second Half of Tenure, which is equal to 1 in the fiscal years "
 "in which the CIO's tenure exceeds one half of the CIO's tenure at departure and 0 otherwise. Conflicted CIOs are defined as in Table III, and the sample is restricted to their plan-years, so the coefficient "
 "compares the second half of a conflicted CIO's tenure with the first half. Tenure at departure is the CIO's tenure in the last fiscal year observed in the plan plus any gap to the departure year. "
 "The performance measure in Panel A is Peer-Adjusted Return, which is the difference of a plan's return and the average pension plan return each year. The performance measure in Panel B is "
 "Benchmark-Adjusted Return, which is calculated as the plan's return minus the return of its policy benchmark, when available. The other independent variables are as defined in Table I. Columns 5 and 6 "
 "include CIO fixed effects and omit the CIO-level controls; Column 6 restricts the sample to CIOs whose tenure at departure is at least four years, so that each half of tenure contains at least two fiscal "
 "years. The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
table_sheet('Table XI','Table XI: Conflicted CIOs: Plan Performance in the First versus Second Half of Tenure',notes1,[('Panel A. Peer-Adjusted Returns','Peer-adj. Ret. (t)','T1A'),('Panel B. Benchmark-Adjusted Returns','Bench-adj. Ret. (t)','T1B')])
notes2=("This table repeats the tests of Table XI with Fee Ratio as the dependent variable. Fee Ratio is the plan's total investment fees as a percentage of plan assets. The sample is restricted to plan-years of "
 "conflicted CIOs, and Second Half of Tenure is equal to 1 in the fiscal years in which the CIO's tenure exceeds one half of the CIO's tenure at departure and 0 otherwise. The other independent variables are as "
 "defined in Table I. Columns 5 and 6 include CIO fixed effects and omit the CIO-level controls; Column 6 restricts the sample to CIOs whose tenure at departure is at least four years. The standard errors are "
 "double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
table_sheet('Table XII','Table XII: Conflicted CIOs: Fee Ratio in the First versus Second Half of Tenure',notes2,[('','Fee Ratio (t)','T2A')])
ws=wb.create_sheet('Table XIII'); ws.sheet_view.showGridLines=False; ws.column_dimensions['A'].width=34
for c in range(2,9): ws.column_dimensions[L(c)].width=13
ws.cell(row=1,column=1,value='Table XIII: Conflicted CIOs: Univariate Comparison of the First and Second Half of Tenure').font=FB
n3=("This table compares the average outcomes of conflicted CIOs in the first and second half of their tenure with one observation per CIO. Plan-years are first averaged within CIO-year for CIOs who run several "
 "plans, then averaged within each half of tenure. Difference is the mean within-CIO change from the first to the second half; the t-statistic tests whether this mean change is zero, and the last column reports "
 "the p-value of a Wilcoxon signed-rank test of the same hypothesis. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws.merge_cells('A2:H2'); ws['A2']=n3; ws['A2'].font=F; ws['A2'].alignment=JUST; ws.row_dimensions[2].height=15*(len(n3)//105+2)
for j,h in enumerate(['','N (CIOs)','First Half','Second Half','Difference','t-stat','% Improving','Wilcoxon p-value'],1):
    cc=ws.cell(row=4,column=j,value=h); cc.font=F; cc.alignment=CENTER; cc.border=Border(top=thin,bottom=thin)
r=5
for p in PR:
    ws.cell(row=r,column=1,value=p['lab']).font=F; ws.cell(row=r,column=2,value=p['n']).font=BLUE
    ws.cell(row=r,column=3,value=p['m1']).font=BLUE; ws.cell(row=r,column=4,value=p['m2']).font=BLUE
    ws.cell(row=r,column=10,value=p['sd']).font=BLUE; ws.cell(row=r,column=11,value=f'=(D{r}-C{r})/(J{r}/SQRT(B{r}))').font=F; ws.cell(row=r,column=12,value=f'=TDIST(ABS(K{r}),B{r}-1,2)').font=F
    ws.cell(row=r,column=5,value=f'=TEXT(D{r}-C{r},"0.000")&IF(L{r}<0.01,"***",IF(L{r}<0.05,"**",IF(L{r}<0.1,"*","")))').font=F
    ws.cell(row=r,column=6,value=f'=TEXT(K{r},"0.00")').font=F
    ws.cell(row=r,column=7,value=p['up']).font=BLUE; ws.cell(row=r,column=7).number_format='0.0%'
    ws.cell(row=r,column=8,value=p['pw']).font=BLUE; ws.cell(row=r,column=8).number_format='0.000'
    for c in [3,4]: ws.cell(row=r,column=c).number_format='0.000'
    for c in range(2,9): ws.cell(row=r,column=c).alignment=RIGHT
    r+=1
for c in range(1,9): ws.cell(row=r-1,column=c).border=Border(bottom=thin)
for j,h in zip([10,11,12],['SD of change','t (helper)','p (helper)']): ws.cell(row=4,column=j,value=h).font=FI
wb.move_sheet('Estimates', offset=3)
out='/home/user/PensionData/referee_response/time_to_departure/conflicted_halves_tables.xlsx'; wb.save(out); print('saved')
for tab in ['T1A','T1B','T2A']:
    print(tab, ' | '.join(f"({i+1}) {r['est']['second'][0]:.3f} (t={r['est']['second'][0]/r['est']['second'][1]:.2f}) N={r['N']}" for i,r in enumerate(TABLES[tab])))
print("paired:", [(p['lab'], p['n'], round(p['m2']-p['m1'],3), round(p['pw'],3)) for p in PR])
