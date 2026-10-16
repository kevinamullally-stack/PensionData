import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
R = pd.read_pickle('interact_res_fye1.pkl'); RES=R['RES']; XV=R['XV']
CP = pd.read_pickle('interact_comp_res.pkl'); COMP=CP['COMP']
CONT = [('Log CIO Total Comp.', COMP['main']), ('Relative CIO Pay (filled)', COMP['relf']), ('CIO Age', COMP['age'])]   # continuous characteristics, centered
NC = len(XV)+len(CONT)  # six binary characteristics + three continuous ones
CI = 1   # column (2) of the fye1 set: all Table III controls + fiscal-year-end date FE
assert RES['underpaid']['peer_adj_ret100'][CI]['col']['ctl']=='All' and RES['underpaid']['peer_adj_ret100'][CI]['col']['fe']=='fye_id'
TNR='Times New Roman'; SZ=10.5
F=Font(name=TNR,size=SZ); FB=Font(name=TNR,size=SZ,bold=True); FI=Font(name=TNR,size=SZ,italic=True); BLUE=Font(name=TNR,size=SZ,color='0000FF')
thin=Side(style='thin'); CENTER=Alignment(horizontal='center',vertical='center',wrap_text=True); RIGHT=Alignment(horizontal='right'); JUST=Alignment(horizontal='justify',wrap_text=True,vertical='top')
LAB = {'underpaid':'Underpaid','young':'Young CIO','priv':'Prior Private Exp.','fin':'Financial Center','rate':'High Discount Rate','fund':'High Funding'}
wb=Workbook(); E=wb.active; E.title='Estimates'
E['A1']='Estimates behind the table. Blue = regression output (coefficient, SE, minimum cluster count). t and p are formulas; p uses the t distribution with (min clusters - 1) df. SE double clustered by plan and fiscal year, with the eigenvalue fix.'; E['A1'].font=FI
for j,h in enumerate(['Variable','Dependent variable','Term','Coefficient','SE','Clusters (min)','t','p'],1): E.cell(row=3,column=j,value=h).font=FB
E.column_dimensions['B'].width=30; E.column_dimensions['C'].width=36
er=[4]
def reg(k,y,term,r,G):
    i=er[0]; er[0]+=1
    for j,v in enumerate([k,y,term],1): E.cell(row=i,column=j,value=v).font=F
    E.cell(row=i,column=4,value=None if np.isnan(r['est']) else r['est']).font=BLUE; E.cell(row=i,column=5,value=None if np.isnan(r['se']) else r['se']).font=BLUE; E.cell(row=i,column=6,value=G).font=BLUE
    E.cell(row=i,column=7,value=f'=IF(AND(ISNUMBER(D{i}),E{i}>0),D{i}/E{i},"")').font=F; E.cell(row=i,column=8,value=f'=IF(G{i}="","",TDIST(ABS(G{i}),F{i}-1,2))').font=F
    for j in [4,5,7,8]: E.cell(row=i,column=j).number_format='0.0000'
    return dict(coef=f'Estimates!D{i}',t=f'Estimates!G{i}',p=f'Estimates!H{i}')
def cf(ref): return f'=IF({ref["p"]}="","",TEXT({ref["coef"]},"0.000")&IF({ref["p"]}<0.01,"***",IF({ref["p"]}<0.05,"**",IF({ref["p"]}<0.1,"*",""))))'
def tf(ref): return f'=IF({ref["t"]}="","","("&TEXT({ref["t"]},"0.00")&")")'
ws=wb.create_sheet('Interactions',0); ws.sheet_view.showGridLines=False; ws.column_dimensions['A'].width=36
for c in range(2,2+NC): ws.column_dimensions[L(c)].width=14
ws.cell(row=1,column=1,value='Table: Conflicted CIOs and Cross-Sectional Characteristics, Interaction Specification').font=FB
note=("This table re-estimates the Table III regression with all control variables and fiscal-year-end date fixed effects, adding a cross-sectional characteristic X and its interaction with Conflicted CIO. Each column uses a different X: Underpaid equals 1 if the CIO's total compensation is below $224,578, the median of CIO pay pooled over fiscal years 2009-2014 (see the Underpaid checks sheet); Young CIO equals 1 for CIOs who are 46 years old or younger; Prior Private Exp. equals 1 for CIOs with prior private firm experience; Financial Center equals 1 for plans headquartered in financial centers; "
      "High Discount Rate equals 1 if the plan's discount rate is above 8%; High Funding equals 1 for plans with a funding ratio of at least 92%; Log CIO Total Comp. is the natural log of the CIO's total compensation in the same fiscal year (CIO_TotalComp), and uses only plan-years with reported compensation. Relative CIO Pay (filled) is log CIO total compensation minus its mean across plan-years in the same fiscal year; in years without reported compensation it takes the value from the CIO's nearest earlier reported year at the same plan, or from the first reported year for earlier years (as the Underpaid measure is filled). CIO Age is the CIO's age in years. The three continuous characteristics are centered at their means in the regression sample, so in those columns Conflicted CIO is the effect of conflict for a CIO with average pay or average age, and Conflicted CIO x X is the change in that effect per log point of pay or per year of age. In the CIO Age column the lagged log CIO age control is dropped, because age enters as X. Young CIO and High Funding are missing when CIO age or the funding ratio is missing. The control variables are those of Table III and have the same coefficients for both groups. Conflicted CIO is the effect of conflict when X = 0, Conflicted CIO x X is the difference between the two groups, and the italic rows report the effect when X = 1 (binary characteristics) or at the 25th and 75th percentiles of X in the regression sample (continuous characteristics). "
      "Panel A uses Peer-Adjusted Return. Panel B uses Benchmark-Adjusted Return computed as the plan's return minus the updated policy benchmark (the benchmark return reported in the plan's financial report or, where none is stated, an inferred value graded A or B). Fiscal-year-end date fixed effects compare plans only with plans whose fiscal year covers the same twelve months. "
      "The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=1+NC); ws['A2']=note; ws['A2'].font=F; ws['A2'].alignment=JUST; ws.row_dimensions[2].height=14*(len(note)//150+2)
r=4
for y,ptitle,dl in [('peer_adj_ret100','Panel A. Peer-Adjusted Returns','Peer-adj. Ret. (t)'),('b_AB','Panel B. Benchmark-Adjusted Returns (updated benchmark)','Bench-adj. Ret. (t)')]:
    ws.cell(row=r,column=1,value=ptitle).font=FB; r+=1
    for j,(k,xv,_) in enumerate(XV): c=ws.cell(row=r,column=2+j,value=f'X = {LAB[k]}'); c.font=F; c.alignment=CENTER; c.border=Border(top=thin)
    for j,(cl,_) in enumerate(CONT): c=ws.cell(row=r,column=2+len(XV)+j,value=f'X = {cl}'); c.font=F; c.alignment=CENTER; c.border=Border(top=thin)
    ws.cell(row=r,column=1).border=Border(top=thin); ws.row_dimensions[r].height=30; r+=1
    for j in range(NC): c=ws.cell(row=r,column=2+j,value=dl); c.font=F; c.alignment=CENTER; c.border=Border(bottom=thin)
    ws.cell(row=r,column=1).border=Border(bottom=thin); r+=1
    def put(col,ref,fnt):
        a=ws.cell(row=r,column=col,value=cf(ref)); a.font=fnt; a.alignment=RIGHT; b=ws.cell(row=r+1,column=col,value=tf(ref)); b.font=fnt; b.alignment=RIGHT
    for term,tl,fnt in [('conf','Conflicted CIO (0/1)',F),('confX','Conflicted CIO x X',F),('X','X',F),('sum','Conflicted CIO effect when X = 1',FI),
                        ('p25','Conflicted CIO effect, 25th pct. of X',FI),('p75','Conflicted CIO effect, 75th pct. of X',FI)]:
        if term=='sum': r+=1
        ws.cell(row=r,column=1,value=tl).font=fnt
        if term in ('conf','confX','X','sum'):
            for j,(k,xv,_) in enumerate(XV):
                x=RES[k][y][CI]; put(2+j, reg(LAB[k],y,tl,x[term],x['G']), fnt)
        if term in ('conf','confX','X','p25','p75'):
            for j,(cl,CV) in enumerate(CONT): put(2+len(XV)+j, reg(cl,y,tl,CV[y][term],CV[y]['G']), fnt)
        r+=2
    r+=1
    for lab,fn,fmt in [('Observations',lambda x:x['N'],'#,##0'),('Adjusted R-squared',lambda x:x['adjr2'],'0.000')]:
        ws.cell(row=r,column=1,value=lab).font=F
        for j,(k,xv,_) in enumerate(XV): c=ws.cell(row=r,column=2+j,value=fn(RES[k][y][CI])); c.font=F; c.alignment=RIGHT; c.number_format=fmt
        for j,(cl,CV) in enumerate(CONT): c=ws.cell(row=r,column=2+len(XV)+j,value=fn(CV[y])); c.font=F; c.alignment=RIGHT; c.number_format=fmt
        r+=1
    for lab in ['Table III Controls','Fiscal-Year-End FE']:
        ws.cell(row=r,column=1,value=lab).font=F
        for j in range(NC): c=ws.cell(row=r,column=2+j,value='Yes'); c.font=F; c.alignment=CENTER
        r+=1
    for c in range(1,2+NC): ws.cell(row=r-1,column=c).border=Border(bottom=thin)
    r+=2
ws.cell(row=r,column=1,value="Coefficients and observations will match reghdfe exactly; t-statistics can differ somewhat. Use the attached Stata code for the exact figures.").font=FI
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=1+NC)

# ---------------- Robustness sheet for the continuous characteristics ----------------
RB=wb.create_sheet('Continuous X robustness',1); RB.sheet_view.showGridLines=False; RB.column_dimensions['A'].width=40
RV=[('main','Log CIO Total Comp. (same year)'),('lag','Lagged Log CIO Total Comp.'),('rel','Log CIO Total Comp. minus fiscal-year mean'),('size','Log CIO Total Comp., plus Conflicted CIO x Size'),
    ('relf_size','Relative CIO Pay (filled), plus Conflicted CIO x Size'),
    ('age','CIO Age (lagged log age control dropped)'),('age_keep','CIO Age (lagged log age control kept)')]
for c in range(2,2+len(RV)): RB.column_dimensions[L(c)].width=15
RB.cell(row=1,column=1,value='Table: Continuous Cross-Sectional Characteristics, Robustness').font=FB
rnote=("Each column re-estimates the interaction regression (all Table III controls, fiscal-year-end date fixed effects) with a continuous X centered at its regression-sample mean. Column (1) and column (6) are the Log CIO Total Comp. and CIO Age columns of the Interactions sheet. "
       "Column (2) uses the prior year's log compensation. Column (3) subtracts the mean log compensation of all plan-years in the same fiscal year, so X measures pay relative to other CIOs that year rather than the rise in pay over the sample period; it uses reported years only (the Relative CIO Pay (filled) column of the Interactions sheet is the filled version). "
       "Column (4) also interacts Conflicted CIO with Size (centered), because compensation rises with plan size; column (5) does the same for Relative CIO Pay (filled). Column (7) keeps the lagged log CIO age control alongside CIO age. "
       "Standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
RB.merge_cells(start_row=2,start_column=1,end_row=2,end_column=1+len(RV)); RB['A2']=rnote; RB['A2'].font=F; RB['A2'].alignment=JUST; RB.row_dimensions[2].height=14*(len(rnote)//125+2)
r=4
for y,ptitle,dl in [('peer_adj_ret100','Panel A. Peer-Adjusted Returns','Peer-adj. Ret. (t)'),('b_AB','Panel B. Benchmark-Adjusted Returns (updated benchmark)','Bench-adj. Ret. (t)')]:
    RB.cell(row=r,column=1,value=ptitle).font=FB; r+=1
    for j,(v,vl) in enumerate(RV): c=RB.cell(row=r,column=2+j,value=f'({j+1})\nX = {vl}'); c.font=F; c.alignment=CENTER; c.border=Border(top=thin)
    RB.cell(row=r,column=1).border=Border(top=thin); RB.row_dimensions[r].height=58; r+=1
    for j in range(len(RV)): c=RB.cell(row=r,column=2+j,value=dl); c.font=F; c.alignment=CENTER; c.border=Border(bottom=thin)
    RB.cell(row=r,column=1).border=Border(bottom=thin); r+=1
    for term,tl,fnt in [('conf','Conflicted CIO (at mean X)',F),('confX','Conflicted CIO x X',F),('X','X',F),('cs','Conflicted CIO x Size',F),
                        ('p25','Conflicted CIO effect, 25th pct. of X',FI),('p75','Conflicted CIO effect, 75th pct. of X',FI)]:
        if term=='p25': r+=1
        RB.cell(row=r,column=1,value=tl).font=fnt
        for j,(v,vl) in enumerate(RV):
            x=COMP[v][y]
            if term=='cs':
                if 'size' not in x['ext']: continue
                est=x['ext']['size']
            else: est=x[term]
            ref=reg('Robustness: '+vl,y,tl,est,x['G'])
            a=RB.cell(row=r,column=2+j,value=cf(ref)); a.font=fnt; a.alignment=RIGHT; b=RB.cell(row=r+1,column=2+j,value=tf(ref)); b.font=fnt; b.alignment=RIGHT
        r+=2
    r+=1
    for lab,fn,fmt in [('Mean of X',lambda x:x['mean'],'0.00'),('25th / 75th pct. of X',lambda x:f"{x['p25v']:.2f} / {x['p75v']:.2f}",'@'),('Observations',lambda x:x['N'],'#,##0'),
                       ('Conflicted plan-years',lambda x:x['nconf'],'#,##0'),('Conflicted CIOs',lambda x:x['ncio'],'#,##0'),('Adjusted R-squared',lambda x:x['adjr2'],'0.000')]:
        RB.cell(row=r,column=1,value=lab).font=F
        for j,(v,vl) in enumerate(RV): c=RB.cell(row=r,column=2+j,value=fn(COMP[v][y])); c.font=F; c.alignment=RIGHT; c.number_format=fmt
        r+=1
    for c in range(1,2+len(RV)): RB.cell(row=r-1,column=c).border=Border(bottom=thin)
    r+=2
RB.cell(row=r,column=1,value="Coefficients and observations will match reghdfe exactly; t-statistics can differ somewhat. Use the attached Stata code for the exact figures.").font=FI

# ---------------- Underpaid checks ----------------
UC=pd.read_pickle('underpaid_check.pkl'); UP=UC['UP']; SPL=pd.read_pickle('underpaid_split_check.pkl')
UQ=wb.create_sheet('Underpaid checks',2); UQ.sheet_view.showGridLines=False; UQ.column_dimensions['A'].width=40
UCOL=[('underpaid','Underpaid as in the paper (pay below $224,578)'),('up_paid_spells','Underpaid as in the paper, spells with reported pay only'),
      ('up_rc','Underpaid, annual median, filled within spell'),('up_rc_raw','Underpaid, annual median, reported years only')]
for c in range(2,2+len(UCOL)): UQ.column_dimensions[L(c)].width=17
UQ.cell(row=1,column=1,value='Table: Alternative Definitions of Underpaid').font=FB
unote=("Underpaid as used in the paper equals 1 when CIO_TotalComp is below $224,578, the median of CIO pay pooled over fiscal years 2009-2014; this holds in all 1,884 plan-years with reported pay. Because pay rises over the sample period, this fixed cutoff classifies 65% of 2001-2008 plan-years as underpaid and 28% of 2015-2020 plan-years. "
       "Column (2) keeps only CIO spells (CIO at a plan) with reported pay in at least one year. Columns (3) and (4) define Underpaid as pay below the median of reported CIO pay in the same fiscal year, as the paper describes; column (3) fills years without reported pay from the CIO's nearest earlier reported year at the same plan (or the first reported year), and column (4) uses reported years only. "
       "Panels A and B use the interaction specification (all Table III controls, fiscal-year-end date fixed effects). Panels C and D use the Table V, Panel A split specification (controls interacted with Underpaid, fiscal-year fixed effects). Standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
UQ.merge_cells(start_row=2,start_column=1,end_row=2,end_column=1+len(UCOL)); UQ['A2']=unote; UQ['A2'].font=F; UQ['A2'].alignment=JUST; UQ.row_dimensions[2].height=14*(len(unote)//95+2)
r=4
def hdr(ptitle,dl,cols):
    global r
    UQ.cell(row=r,column=1,value=ptitle).font=FB; r+=1
    for j,(v,vl) in enumerate(cols): c=UQ.cell(row=r,column=2+j,value=f'({j+1})\n{vl}'); c.font=F; c.alignment=CENTER; c.border=Border(top=thin)
    UQ.cell(row=r,column=1).border=Border(top=thin); UQ.row_dimensions[r].height=58; r+=1
    for j in range(len(cols)): c=UQ.cell(row=r,column=2+j,value=dl); c.font=F; c.alignment=CENTER; c.border=Border(bottom=thin)
    UQ.cell(row=r,column=1).border=Border(bottom=thin); r+=1
def rowpair(tl,fnt,items):
    global r
    UQ.cell(row=r,column=1,value=tl).font=fnt
    for j,(lab,est,G) in enumerate(items):
        if est is None: continue
        ref=reg(lab,'',tl,est,G); a=UQ.cell(row=r,column=2+j,value=cf(ref)); a.font=fnt; a.alignment=RIGHT; b=UQ.cell(row=r+1,column=2+j,value=tf(ref)); b.font=fnt; b.alignment=RIGHT
    r+=2
def foot(rows,ncol):
    global r
    for lab,vals,fmt in rows:
        UQ.cell(row=r,column=1,value=lab).font=F
        for j,v in enumerate(vals): c=UQ.cell(row=r,column=2+j,value=v); c.font=F; c.alignment=RIGHT; c.number_format=fmt
        r+=1
    for c in range(1,2+ncol): UQ.cell(row=r-1,column=c).border=Border(bottom=thin)
    r+=2
for y,ptitle,dl in [('peer_adj_ret100','Panel A. Interaction specification, Peer-Adjusted Returns','Peer-adj. Ret. (t)'),('b_AB','Panel B. Interaction specification, Benchmark-Adjusted Returns (updated benchmark)','Bench-adj. Ret. (t)')]:
    hdr(ptitle,dl,UCOL)
    for term,tl,fnt in [('conf','Conflicted CIO (0/1)',F),('confX','Conflicted CIO x Underpaid',F),('X','Underpaid (0/1)',F),('sum','Conflicted CIO effect when Underpaid = 1',FI)]:
        if term=='sum': r+=1
        rowpair(tl,fnt,[(f'Underpaid check: {vl} [{y}]',UP[v][y][term],UP[v][y]['G']) for v,vl in UCOL])
    r+=1
    foot([('Observations',[UP[v][y]['N'] for v,_ in UCOL],'#,##0'),('Share Underpaid, all / conflicted',[f"{UP[v][y]['share1']:.2f} / {UP[v][y]['share1_conf']:.2f}" for v,_ in UCOL],'@'),('Adjusted R-squared',[UP[v][y]['adjr2'] for v,_ in UCOL],'0.000')],len(UCOL))
SCOL=[c for c in UCOL if c[0]!='up_paid_spells']
for y,ptitle,dl in [('peer_adj_ret100','Panel C. Table V, Panel A split specification, Peer-Adjusted Returns','Peer-adj. Ret. (t)'),('b_AB','Panel D. Table V, Panel A split specification, Benchmark-Adjusted Returns (updated benchmark)','Bench-adj. Ret. (t)')]:
    hdr(ptitle,dl,SCOL)
    rowpair('Underpaid x Conflicted CIO',F,[(f'Split check: {vl} [{y}]',SPL[(v,y)]['a'],SPL[(v,y)]['G']) for v,vl in SCOL])
    rowpair('Not Underpaid x Conflicted CIO',F,[(f'Split check: {vl} [{y}]',SPL[(v,y)]['b'],SPL[(v,y)]['G']) for v,vl in SCOL])
    rowpair('Difference',FI,[(f'Split check: {vl} [{y}]',SPL[(v,y)]['d'],SPL[(v,y)]['G']) for v,vl in SCOL])
    foot([('p-value of difference',[SPL[(v,y)]['d']['p'] for v,_ in SCOL],'0.000'),('Observations',[SPL[(v,y)]['N'] for v,_ in SCOL],'#,##0')],len(SCOL))
UQ.cell(row=r,column=1,value="Coefficients and observations will match reghdfe exactly; t-statistics can differ somewhat. Use the attached Stata code for the exact figures.").font=FI
for sh in (ws,RB,UQ):
    sh.page_setup.orientation='landscape'; sh.sheet_properties.pageSetUpPr.fitToPage=True; sh.page_setup.fitToWidth=1; sh.page_setup.fitToHeight=0
out='/home/user/PensionData/referee_response/time_to_departure/xsec_interactions_fye1.xlsx'; wb.save(out); print('saved')
# compact results file
lines=["# Interaction specification: all Table III controls + fye1 FE; SE plan & year; t in parentheses"]
for y,yl in [('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark'),('bench_adj_ret_pct','Benchmark-adjusted, original benchmark'),('b_docAB','Benchmark-adjusted, updated benchmark, document-matched')]:
    lines.append(f"\n## {yl}")
    for k,xv,_ in XV:
        x=RES[k][y][CI]; lines.append(f"{LAB[k]:20s} conf {x['conf']['est']:.3f} ({x['conf']['t']:.2f}) | conf x X {x['confX']['est']:.3f} ({x['confX']['t']:.2f}) | X {x['X']['est']:.3f} ({x['X']['t']:.2f}) | effect X=1 {x['sum']['est']:.3f} ({x['sum']['t']:.2f}) | N {x['N']}")
    for cl,v in [('Log CIO Total Comp.','main'),('  lagged','lag'),('  minus FY mean','rel'),('  + Conf x Size','size'),('Rel. pay (filled)','relf'),('  + Conf x Size','relf_size'),('CHECK underpaid@relf','up_on_relf'),('CIO Age','age'),('  log age ctrl kept','age_keep')]:
        x=COMP[v][y]; lines.append(f"{cl:20s} conf@mean {x['conf']['est']:.3f} ({x['conf']['t']:.2f}) | conf x X {x['confX']['est']:.3f} ({x['confX']['t']:.2f}) | X {x['X']['est']:.3f} ({x['X']['t']:.2f}) | effect p25 {x['p25']['est']:.3f} ({x['p25']['t']:.2f}) p75 {x['p75']['est']:.3f} ({x['p75']['t']:.2f}) | N {x['N']}")
lines.append("\n## Underpaid checks (interaction spec: all controls + fye1 FE)")
for v,vl in UCOL:
    for y in ['peer_adj_ret100','b_AB']:
        x=UP[v][y]; lines.append(f"{vl[:58]:58s} {y[:6]:6s} conf {x['conf']['est']:.3f} ({x['conf']['t']:.2f}) | conf x UP {x['confX']['est']:.3f} ({x['confX']['t']:.2f}) | UP=1 {x['sum']['est']:.3f} ({x['sum']['t']:.2f}) | N {x['N']}")
lines.append("\n## Underpaid checks (Table V-A split spec, fy FE)")
for v,vl in SCOL:
    for y in ['peer_adj_ret100','b_AB']:
        x=SPL[(v,y)]; lines.append(f"{vl[:58]:58s} {y[:6]:6s} UP x conf {x['a']['est']:.3f} ({x['a']['t']:.2f}) | not UP x conf {x['b']['est']:.3f} ({x['b']['t']:.2f}) | diff p {x['d']['p']:.3f} | N {x['N']}")
open('/home/user/PensionData/referee_response/time_to_departure/results_xsec_interactions_fye1.md','w').write('\n'.join(lines)); print('\n'.join(lines))
