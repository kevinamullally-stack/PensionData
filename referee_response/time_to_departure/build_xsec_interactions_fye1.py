import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
R = pd.read_pickle('interact_res_fye1.pkl'); RES=R['RES']; XV=R['XV']
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
for c in range(2,8): ws.column_dimensions[L(c)].width=14
ws.cell(row=1,column=1,value='Table: Conflicted CIOs and Cross-Sectional Characteristics, Interaction Specification').font=FB
note=("This table re-estimates the Table III regression with all control variables and fiscal-year-end date fixed effects, adding a cross-sectional characteristic X and its interaction with Conflicted CIO. Each column uses a different X: Underpaid equals 1 if the CIO is underpaid relative to the size of the plan; Young CIO equals 1 for CIOs who are 46 years old or younger; Prior Private Exp. equals 1 for CIOs with prior private firm experience; Financial Center equals 1 for plans headquartered in financial centers; "
      "High Discount Rate equals 1 if the plan's discount rate is above 8%; High Funding equals 1 for plans with a funding ratio of at least 92%. Young CIO and High Funding are missing when CIO age or the funding ratio is missing. The control variables are those of Table III and have the same coefficients for both groups. Conflicted CIO is the effect of conflict when X = 0, Conflicted CIO x X is the difference between the two groups, and the italic row reports the effect when X = 1. "
      "Panel A uses Peer-Adjusted Return. Panel B uses Benchmark-Adjusted Return computed as the plan's return minus the updated policy benchmark (the benchmark return reported in the plan's financial report or, where none is stated, an inferred value graded A or B). Fiscal-year-end date fixed effects compare plans only with plans whose fiscal year covers the same twelve months. "
      "The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws.merge_cells('A2:G2'); ws['A2']=note; ws['A2'].font=F; ws['A2'].alignment=JUST; ws.row_dimensions[2].height=15*(len(note)//100+2)
r=4
for y,ptitle,dl in [('peer_adj_ret100','Panel A. Peer-Adjusted Returns','Peer-adj. Ret. (t)'),('b_AB','Panel B. Benchmark-Adjusted Returns (updated benchmark)','Bench-adj. Ret. (t)')]:
    ws.cell(row=r,column=1,value=ptitle).font=FB; r+=1
    for j,(k,xv,_) in enumerate(XV): c=ws.cell(row=r,column=2+j,value=f'X = {LAB[k]}'); c.font=F; c.alignment=CENTER; c.border=Border(top=thin)
    ws.cell(row=r,column=1).border=Border(top=thin); ws.row_dimensions[r].height=30; r+=1
    for j in range(len(XV)): c=ws.cell(row=r,column=2+j,value=dl); c.font=F; c.alignment=CENTER; c.border=Border(bottom=thin)
    ws.cell(row=r,column=1).border=Border(bottom=thin); r+=1
    for term,tl,fnt in [('conf','Conflicted CIO (0/1)',F),('confX','Conflicted CIO x X',F),('X','X (0/1)',F),('sum','Conflicted CIO effect when X = 1',FI)]:
        if term=='sum': r+=1
        ws.cell(row=r,column=1,value=tl).font=fnt
        for j,(k,xv,_) in enumerate(XV):
            x=RES[k][y][CI]; ref=reg(LAB[k],y,tl,x[term],x['G'])
            a=ws.cell(row=r,column=2+j,value=cf(ref)); a.font=fnt; a.alignment=RIGHT; b=ws.cell(row=r+1,column=2+j,value=tf(ref)); b.font=fnt; b.alignment=RIGHT
        r+=2
    r+=1
    for lab,fn,fmt in [('Observations',lambda x:x['N'],'#,##0'),('Adjusted R-squared',lambda x:x['adjr2'],'0.000')]:
        ws.cell(row=r,column=1,value=lab).font=F
        for j,(k,xv,_) in enumerate(XV): c=ws.cell(row=r,column=2+j,value=fn(RES[k][y][CI])); c.font=F; c.alignment=RIGHT; c.number_format=fmt
        r+=1
    for lab in ['Table III Controls','Fiscal-Year-End FE']:
        ws.cell(row=r,column=1,value=lab).font=F
        for j in range(len(XV)): c=ws.cell(row=r,column=2+j,value='Yes'); c.font=F; c.alignment=CENTER
        r+=1
    for c in range(1,8): ws.cell(row=r-1,column=c).border=Border(bottom=thin)
    r+=2
ws.cell(row=r,column=1,value="Coefficients and observations will match reghdfe exactly; t-statistics can differ somewhat. Use the attached Stata code for the exact figures.").font=FI
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=7)
out='/home/user/PensionData/referee_response/time_to_departure/xsec_interactions_fye1.xlsx'; wb.save(out); print('saved')
# compact results file
lines=["# Interaction specification: all Table III controls + fye1 FE; SE plan & year; t in parentheses"]
for y,yl in [('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark'),('bench_adj_ret_pct','Benchmark-adjusted, original benchmark'),('b_docAB','Benchmark-adjusted, updated benchmark, document-matched')]:
    lines.append(f"\n## {yl}")
    for k,xv,_ in XV:
        x=RES[k][y][CI]; lines.append(f"{LAB[k]:20s} conf {x['conf']['est']:.3f} ({x['conf']['t']:.2f}) | conf x X {x['confX']['est']:.3f} ({x['confX']['t']:.2f}) | X {x['X']['est']:.3f} ({x['X']['t']:.2f}) | effect X=1 {x['sum']['est']:.3f} ({x['sum']['t']:.2f}) | N {x['N']}")
open('/home/user/PensionData/referee_response/time_to_departure/results_xsec_interactions_fye1.md','w').write('\n'.join(lines)); print('\n'.join(lines))
