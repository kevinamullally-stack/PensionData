import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
RES = pd.read_pickle('bench_compare_res.pkl')
TNR='Times New Roman'; SZ=10.5
F=Font(name=TNR,size=SZ); FB=Font(name=TNR,size=SZ,bold=True); FI=Font(name=TNR,size=SZ,italic=True); BLUE=Font(name=TNR,size=SZ,color='0000FF')
thin=Side(style='thin'); CENTER=Alignment(horizontal='center',vertical='center',wrap_text=True); RIGHT=Alignment(horizontal='right'); JUST=Alignment(horizontal='justify',wrap_text=True,vertical='top')
wb=Workbook(); E=wb.active; E.title='Estimates'
E['A1']='Estimates behind the tables: blue = regression output (coefficient, SE, min cluster count); t, p and stars in the tables are formulas. SE double clustered by plan and fiscal year, PSD-corrected; p from t distribution with (min clusters - 1) df.'; E['A1'].font=FI
for j,h in enumerate(['Table','Row','Column','Coefficient','SE','Clusters (min)','t','p'],1): c=E.cell(row=3,column=j,value=h); c.font=FB
E.column_dimensions['A'].width=10; E.column_dimensions['B'].width=48; E.column_dimensions['C'].width=26
erow=[4]
def reg(table,row,col,est,se,G):
    r=erow[0]; erow[0]+=1
    E.cell(row=r,column=1,value=table).font=F; E.cell(row=r,column=2,value=row).font=F; E.cell(row=r,column=3,value=col).font=F
    E.cell(row=r,column=4,value=None if (est is None or np.isnan(est)) else float(est)).font=BLUE; E.cell(row=r,column=5,value=None if (se is None or np.isnan(se)) else float(se)).font=BLUE; E.cell(row=r,column=6,value=int(G)).font=BLUE
    E.cell(row=r,column=7,value=f'=IF(AND(ISNUMBER(D{r}),E{r}>0),D{r}/E{r},"")').font=F; E.cell(row=r,column=8,value=f'=IF(G{r}="","",TDIST(ABS(G{r}),F{r}-1,2))').font=F
    for j in [4,5,7,8]: E.cell(row=r,column=j).number_format='0.0000'
    return dict(coef=f'Estimates!D{r}',t=f'Estimates!G{r}',p=f'Estimates!H{r}')
def coef_f(ref): return f'=IF({ref["p"]}="","n/a",TEXT({ref["coef"]},"0.000")&IF({ref["p"]}<0.01,"***",IF({ref["p"]}<0.05,"**",IF({ref["p"]}<0.1,"*",""))))'
def t_f(ref): return f'=IF({ref["t"]}="","","("&TEXT({ref["t"]},"0.00")&")")'
def p_f(ref): return f'=IF({ref["p"]}="","",{ref["p"]})'
def sheet(name,title,notes,width=7):
    ws=wb.create_sheet(name); ws.sheet_view.showGridLines=False; ws.column_dimensions['A'].width=36
    for c in range(2,2+width): ws.column_dimensions[L(c)].width=15
    ws.cell(row=1,column=1,value=title).font=FB; ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=1+width); ws.cell(row=2,column=1,value=notes).font=F; ws.cell(row=2,column=1).alignment=JUST; ws.row_dimensions[2].height=15*(len(notes)//100+2)
    return ws
def hdr(ws,r,labels,top=True):
    for j,l in enumerate(labels): c=ws.cell(row=r,column=2+j,value=l); c.font=F; c.alignment=CENTER; c.border=Border(top=thin if top else None, bottom=thin)
    ws.cell(row=r,column=1).border=Border(top=thin if top else None, bottom=thin)
def pair(ws,r,c,ref): 
    x=ws.cell(row=r,column=c,value=coef_f(ref)); x.font=F; x.alignment=RIGHT; y=ws.cell(row=r+1,column=c,value=t_f(ref)); y.font=F; y.alignment=RIGHT
def bottom(ws,r,ncol):
    for c in range(1,2+ncol): ws.cell(row=r,column=c).border=Border(bottom=thin)
G_MIN = 20   # min clusters = fiscal years (20) in every regression here; plan clusters are >= 86
LAB={'conf_pen_vendor':'Conflicted CIO (0/1)','t_eq':'Equity Target Allocation (%)','t_fi':'Fixed Income Target Allocation (%)','t_re':'Real Estate Target Allocation (%)','t_pe':'Private Equity Target Allocation (%)','t_hf':'Hedge Fund Target Allocation (%)','t_alt':'Misc. Alternatives Target Allocation (%)','t_comd':'Commodities Target Allocation (%)',
 'l_invret':'Investment Return (t - 1)','size':'Log (Plan Size) (t-1)','l_fund':'Funding Ratio (t-1)','fincenter1':'Financial Center (0/1)','l_log_cio_age':'Log (CIO Age) (t-1)','l_log_cio_tenure':'Log (CIO Tenure) (t-1)','prior_private_exp':'CIO Prior Private Experience (0/1)','Elite_inst':'CIO Attended Elite College (0/1)','l_sib1':'Separate Investment Board (0/1)','wstate_political':'% Political Appointees on Board'}
# ---------- Table B1
n1=("This table reports results of tests that regress the return of a plan's total-fund policy benchmark on Conflicted CIO, which is equal to 1 for all years prior to the plan's investment officer's departure for a position with a pension plan vendor and 0 otherwise. "
 "The dependent variable is the fiscal-year return of the plan's policy benchmark, in percent, as reported in the plan's financial statements. All columns include fiscal-year-end date fixed effects, so plans are compared only with plans whose fiscal year covers the same twelve months. "
 "Columns 2 to 4 add the plan's target allocation to each asset class (cash omitted), and Columns 3 and 4 add the control variables of Table III. Column 4 adds plan fixed effects. The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws=sheet('Table B1','Table B1: Policy Benchmark Returns of Conflicted and Unconflicted CIOs',n1,4); r=4
hdr(ws,r,[f'({i+1})' for i in range(4)]); r+=1; hdr(ws,r,['Benchmark Ret. (t)']*4,top=False); r+=1
rows=['conf_pen_vendor']+[k for k in LAB if k!='conf_pen_vendor']
for v in rows:
    if not any(v in reg_['est'] for reg_ in RES['B1']): continue
    ws.cell(row=r,column=1,value=LAB[v]).font=F
    for j,reg_ in enumerate(RES['B1']):
        if v in reg_['est']: pair(ws,r,2+j,reg(f'B1',LAB[v],reg_['col'],*reg_['est'][v],G_MIN))
    r+=2
r+=1
for lab,vals in [('Observations',[x['N'] for x in RES['B1']]),('Adjusted R-squared',[x['adjr2'] for x in RES['B1']]),('Target Allocation Controls',[x['tw'] for x in RES['B1']]),('Table III Controls',['No','No','Yes','Yes']),('Plan FE',[x['pfe'] for x in RES['B1']]),('Fiscal-Year-End FE',['Yes']*4)]:
    ws.cell(row=r,column=1,value=lab).font=F
    for j,v in enumerate(vals):
        c=ws.cell(row=r,column=2+j,value=v); c.font=F; c.alignment=RIGHT if isinstance(v,(int,float)) else CENTER
        if lab=='Observations': c.number_format='#,##0'
        if lab=='Adjusted R-squared': c.number_format='0.000'
    r+=1
bottom(ws,r-1,4)
# ---------- Table B2
n2=("This table reports results of tests that divide the sample into the cross-sectional groups of Tables V to VII and regress the return of a plan's total-fund policy benchmark, in percent, on Conflicted CIO interacted with the group indicator. Each row is a separate regression in which all control variables are also interacted with the group indicator, as in Tables V to VII. "
 "Panel A uses the control variables of the corresponding table in the paper. Panel B adds the plan's target allocation to each asset class, interacted with the group indicator. All regressions include fiscal-year-end date fixed effects. The last column reports the p-value of a test that the two coefficients are equal. The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws=sheet('Table B2','Table B2: Policy Benchmark Returns of Conflicted CIOs by Cross-Sectional Group',n2,5); r=4
for spec,ptitle in [('A','Panel A. Without target allocation controls'),('B','Panel B. With target allocation controls')]:
    ws.cell(row=r,column=1,value=ptitle).font=FB; r+=1
    hdr(ws,r,['Group x Conflicted','Other Group x Conflicted','p-value: equal','Observations','Adj. R-squared']); r+=1
    for x in RES['B2'][spec]:
        ws.cell(row=r,column=1,value=f"{x['name']}: {x['l1']} vs. {x['l0']}").font=F
        pair(ws,r,2,reg(f'B2{spec}',x['name'],'group x conf',x['a']['est'],x['a']['se'],G_MIN)); pair(ws,r,3,reg(f'B2{spec}',x['name'],'other x conf',x['b']['est'],x['b']['se'],G_MIN))
        rd=reg(f'B2{spec}',x['name'],'difference',x['d']['est'],x['d']['se'],G_MIN); c=ws.cell(row=r,column=4,value=p_f(rd)); c.font=F; c.alignment=RIGHT; c.number_format='0.000'
        c=ws.cell(row=r,column=5,value=x['N']); c.font=F; c.alignment=RIGHT; c.number_format='#,##0'; c=ws.cell(row=r,column=6,value=x['adjr2']); c.font=F; c.alignment=RIGHT; c.number_format='0.000'
        r+=2
    bottom(ws,r-1,5); r+=1
# ---------- Table B3
n3=("This table restricts the sample to plan-years run by conflicted CIOs and regresses the return of the plan's total-fund policy benchmark, in percent, on the cross-sectional group indicator. Column 1 includes only fiscal-year-end date fixed effects; Column 2 adds the plan's target allocation to each asset class; Column 3 adds the control variables of Table III. "
 "A negative coefficient means that conflicted CIOs in the group run plans whose policy benchmarks returned less than those of other conflicted CIOs with the same fiscal-year end. The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws=sheet('Table B3','Table B3: Policy Benchmark Returns among Conflicted CIOs, by Cross-Sectional Group',n3,3); r=4
hdr(ws,r,['(1)','(2)','(3)']); r+=1; hdr(ws,r,['Benchmark Ret. (t)']*3,top=False); r+=1
for x in RES['B3']:
    ws.cell(row=r,column=1,value=f"{x['l1']} (0/1)").font=F
    for j,cc in enumerate(x['cols']): pair(ws,r,2+j,reg('B3',x['l1'],f'({j+1})',cc['r']['est'],cc['r']['se'],G_MIN))
    ws.cell(row=r+2,column=1,value='   Observations').font=FI
    for j,cc in enumerate(x['cols']): c=ws.cell(row=r+2,column=2+j,value=cc['N']); c.font=FI; c.alignment=RIGHT
    r+=3
for lab,vals in [('Target Allocation Controls',['No','Yes','Yes']),('Table III Controls',['No','No','Yes']),('Fiscal-Year-End FE',['Yes']*3)]:
    ws.cell(row=r,column=1,value=lab).font=F
    for j,v in enumerate(vals): c=ws.cell(row=r,column=2+j,value=v); c.font=F; c.alignment=CENTER
    r+=1
bottom(ws,r-1,3)
# ---------- Table B4
n4=("This table regresses the fiscal-year return of the benchmark index each plan designates for an asset class, in percent, on Conflicted CIO. Asset-class benchmark returns are collected from plans' financial reports. Column 1 includes only fiscal-year-end date fixed effects; Column 2 adds the plan's target allocation to each asset class and the control variables of Table III. "
 "A negative coefficient means that conflicted CIOs' plans designate indexes for that asset class that returned less than the indexes designated by other plans with the same fiscal-year end. The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws=sheet('Table B4','Table B4: Asset-Class Benchmark Returns of Conflicted and Unconflicted CIOs',n4,4); r=4
hdr(ws,r,['(1) No controls','Observations','(2) With controls','Observations']); r+=1
for x in RES['B4']:
    ws.cell(row=r,column=1,value=x['lab']).font=F
    for j,cc in enumerate(x['cols']):
        pair(ws,r,2+2*j,reg('B4',x['lab'],f'({j+1})',cc['r']['est'],cc['r']['se'],G_MIN)); c=ws.cell(row=r,column=3+2*j,value=cc['N']); c.font=F; c.alignment=RIGHT; c.number_format='#,##0'
    r+=2
ws.cell(row=r,column=1,value='Fiscal-Year-End FE').font=F
for j in [2,4]: c=ws.cell(row=r,column=j,value='Yes'); c.font=F; c.alignment=CENTER
bottom(ws,r,4)
# ---------- Table B5
n5=("This table repeats the tests of Table B4 within the cross-sectional groups of Tables V to VII. Each row is a separate regression of the asset-class benchmark return, in percent, on Conflicted CIO interacted with the group indicator, with the plan's target allocations and the corresponding table's control variables also interacted with the group indicator, and fiscal-year-end date fixed effects. "
 "The last column reports the p-value of a test that the two coefficients are equal. The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws=sheet('Table B5','Table B5: Asset-Class Benchmark Returns of Conflicted CIOs by Cross-Sectional Group',n5,4); r=4
for name,rows_ in RES['B5'].items():
    l1=rows_[0]['l1']; l0=rows_[0]['l0']
    ws.cell(row=r,column=1,value=f'Panel: {name}').font=FB; r+=1
    hdr(ws,r,[f'{l1} x Conflicted',f'{l0} x Conflicted','p-value: equal','Observations']); r+=1
    for x in rows_:
        ws.cell(row=r,column=1,value=x['lab']).font=F
        pair(ws,r,2,reg('B5',f"{name}: {x['lab']}",'group x conf',x['a']['est'],x['a']['se'],G_MIN)); pair(ws,r,3,reg('B5',f"{name}: {x['lab']}",'other x conf',x['b']['est'],x['b']['se'],G_MIN))
        rd=reg('B5',f"{name}: {x['lab']}",'difference',x['d']['est'],x['d']['se'],G_MIN); c=ws.cell(row=r,column=4,value=p_f(rd)); c.font=F; c.alignment=RIGHT; c.number_format='0.000'
        c=ws.cell(row=r,column=5,value=x['N']); c.font=F; c.alignment=RIGHT; c.number_format='#,##0'
        r+=2
    bottom(ws,r-1,4); r+=1
wb.move_sheet('Estimates', offset=5)
out='/home/user/PensionData/referee_response/time_to_departure/benchmark_return_tables.xlsx'; wb.save(out); print('saved')
