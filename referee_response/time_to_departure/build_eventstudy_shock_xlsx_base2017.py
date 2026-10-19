import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
R=pd.read_pickle('es_shock_b2017.pkl'); ES=R['ES']; EV=R['EV']; YS=R['YS']; SPECS=R['SPECS']
TNR='Times New Roman'; SZ=10.5
F=Font(name=TNR,size=SZ); FB=Font(name=TNR,size=SZ,bold=True); FI=Font(name=TNR,size=SZ,italic=True); BLUE=Font(name=TNR,size=SZ,color='0000FF')
thin=Side(style='thin'); CENTER=Alignment(horizontal='center',vertical='center',wrap_text=True); RIGHT=Alignment(horizontal='right'); JUST=Alignment(horizontal='justify',wrap_text=True,vertical='top')
wb=Workbook(); E=wb.active; E.title='Estimates'
E['A1']='Estimates behind the table. Blue = regression output (coefficient, SE, minimum cluster count). t and p are formulas; p uses the t distribution with (min clusters - 1) df. SE double clustered by plan and year, with the eigenvalue fix.'; E['A1'].font=FI
for j,h in enumerate(['Dependent variable','Specification','Term','Coefficient','SE','Clusters (min)','t','p'],1): E.cell(row=3,column=j,value=h).font=FB
for c,w in zip('ABC',[44,20,16]): E.column_dimensions[c].width=w
er=[4]
def reg(y,spec,term,r,G):
    i=er[0]; er[0]+=1
    for j,v in enumerate([y,spec,term],1): E.cell(row=i,column=j,value=v).font=F
    E.cell(row=i,column=4,value=r['est']).font=BLUE; E.cell(row=i,column=5,value=r['se']).font=BLUE; E.cell(row=i,column=6,value=G).font=BLUE
    E.cell(row=i,column=7,value=f'=IF(E{i}>0,D{i}/E{i},"")').font=F; E.cell(row=i,column=8,value=f'=IF(G{i}="","",TDIST(ABS(G{i}),F{i}-1,2))').font=F
    for j in [4,5,7,8]: E.cell(row=i,column=j).number_format='0.0000'
    return dict(coef=f'Estimates!D{i}',t=f'Estimates!G{i}',p=f'Estimates!H{i}')
def cf(ref): return f'=IF({ref["p"]}="","",TEXT({ref["coef"]},"0.000")&IF({ref["p"]}<0.01,"***",IF({ref["p"]}<0.05,"**",IF({ref["p"]}<0.1,"*",""))))'
def tf(ref): return f'=IF({ref["t"]}="","","("&TEXT({ref["t"]},"0.00")&")")'
ws=wb.create_sheet('Event study',0); ws.sheet_view.showGridLines=False; ws.column_dimensions['A'].width=38
for c in range(2,9): ws.column_dimensions[L(c)].width=13
ws.column_dimensions['E'].width=3
ws['A1']='Table 5b: Event Study of Conflicted CIO Performance Around the Loglisci Shock (FY2017 Base Year)'; ws['A1'].font=FB
note=("This table re-estimates the Table 5b event study for Peer-Adjusted Return and for Benchmark-Adjusted Return (the plan's return minus the updated policy benchmark: the benchmark return reported in the plan's financial report or, where none is stated, an inferred value graded A or B). "
      "Each regression includes Conflicted CIO interacted with indicators for fiscal years 2005-2016 (FY2017 is the omitted base year), and endpoint bins for Conflicted CIO in years before 2005 and after 2017; there is no standalone Conflicted CIO term, so each coefficient is the effect of conflict in that year relative to FY2017. "
      "The control variables are those in effect at Table 5b in the paper's code: the lagged return, Size, the lagged funding ratio, lagged allocations, Financial Center, lagged log CIO age and tenure, lagged sibling plans and the political-state indicator. "
      "The tests group the coefficients by the timing of the shock: pre-shock (the pre-2005 bin and FY2005-2008), shock period (FY2009-2013, when shock2 = 1) and late period (FY2014-2016 and the post-2017 bin). 'Pre-shock equal' tests that the pre-shock coefficients are equal to each other. 'Pre-shock minus shock period' is the mean of the FY2005-2008 coefficients minus the mean of the FY2009-2013 coefficients, which does not depend on the choice of base year. "
      "The standard errors are double clustered by plan and year. Coefficients marked with ***, **, and * are significant at the 1%, 5%, and 10% level, respectively.")
ws.merge_cells('A2:H2'); ws['A2']=note; ws['A2'].font=F; ws['A2'].alignment=JUST; ws.row_dimensions[2].height=14*(len(note)//115+2)
r=4
cols={}
for j,(y,yl) in enumerate(YS):
    c0=2+4*j; ws.merge_cells(start_row=r,start_column=c0,end_row=r,end_column=c0+2); c=ws.cell(row=r,column=c0,value=yl); c.font=F; c.alignment=CENTER
    for k in range(3): ws.cell(row=r,column=c0+k).border=Border(top=thin)
    for k,(fe,sl) in enumerate(SPECS): cols[(y,fe)]=c0+k
ws.cell(row=r,column=1).border=Border(top=thin); ws.row_dimensions[r].height=30; r+=1
for (y,fe),c in cols.items():
    x=ws.cell(row=r,column=c,value=dict(SPECS)[fe]); x.font=F; x.alignment=CENTER; x.border=Border(bottom=thin)
ws.cell(row=r,column=1).border=Border(bottom=thin); ws.row_dimensions[r].height=30; r+=1
LAB={'pre_bin':'Conflicted CIO x FY<2005','post_bin':'Conflicted CIO x FY>2017'}
for v in EV:
    ws.cell(row=r,column=1,value=LAB.get(v, 'Conflicted CIO x FY'+v[-4:])).font=F
    for (y,fe),c in cols.items():
        x=ES[(y,fe)]; ref=reg(dict(YS)[y],dict(SPECS)[fe],v,x['coef'][v],x['G'])
        a=ws.cell(row=r,column=c,value=cf(ref)); a.font=F; a.alignment=RIGHT; b=ws.cell(row=r+1,column=c,value=tf(ref)); b.font=F; b.alignment=RIGHT
    r+=2
r+=1
ws.cell(row=r,column=1,value='Pre-shock minus shock period').font=FI
for (y,fe),c in cols.items():
    x=ES[(y,fe)]; ref=reg(dict(YS)[y],dict(SPECS)[fe],'pre-shock minus shock period',x['contrast'],x['G'])
    a=ws.cell(row=r,column=c,value=cf(ref)); a.font=FI; a.alignment=RIGHT; b=ws.cell(row=r+1,column=c,value=tf(ref)); b.font=FI; b.alignment=RIGHT
r+=3
for lab,fn,fmt in [('p-value: pre-shock jointly zero',lambda x:x['pre']['p'],'0.000'),('p-value: pre-shock equal',lambda x:x['preflat']['p'],'0.000'),('p-value: shock period jointly zero',lambda x:x['shock']['p'],'0.000'),('p-value: late period jointly zero',lambda x:x['late']['p'],'0.000'),
                   ('Observations',lambda x:x['N'],'#,##0'),('Adjusted R-squared',lambda x:x['adjr2'],'0.000')]:
    ws.cell(row=r,column=1,value=lab).font=F
    for (y,fe),c in cols.items(): x=ws.cell(row=r,column=c,value=fn(ES[(y,fe)])); x.font=BLUE if 'p-value' in lab else F; x.alignment=RIGHT; x.number_format=fmt
    r+=1
for lab,vals in [('Plan FE',['No','Yes','Yes']),('Year FE',['Yes','No','Yes'])]:
    ws.cell(row=r,column=1,value=lab).font=F
    for (y,fe),c in cols.items(): x=ws.cell(row=r,column=c,value=vals[[f for f,_ in SPECS].index(fe)]); x.font=F; x.alignment=CENTER
    r+=1
for c in range(1,9): ws.cell(row=r-1,column=c).border=Border(bottom=thin)
r+=1
ws.cell(row=r,column=1,value="Blue p-values are F-tests computed from the two-way clustered covariance (denominator df = clusters - 1). Coefficients and observations will match reghdfe; t-statistics and p-values can differ somewhat. Use the attached Stata code for the exact figures.").font=FI
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=8); ws.cell(row=r,column=1).alignment=JUST; ws.row_dimensions[r].height=30
ws.page_setup.orientation='landscape'; ws.sheet_properties.pageSetUpPr.fitToPage=True; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0
out='/home/user/PensionData/referee_response/time_to_departure/eventstudy_shock_tables_base2017.xlsx'; wb.save(out); print('saved',out)
