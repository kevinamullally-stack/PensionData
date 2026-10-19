import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=pd.read_pickle('es_shock_b2017.pkl'); ES=R['ES']; YRS=R['YRS']; BASE=R['BASE']; SH0,SH1=R['SHOCK']
BLUE='#2a78d6'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; SURF='#ffffff'; BAND='#f1f0ec'
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':10.5,'axes.edgecolor':INK2,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2})
fe='ppd_id + fy'
panels=[('peer_adj_ret100','A. Peer-adjusted return'),('b_AB','B. Benchmark-adjusted return (updated benchmark)')]
fig,axes=plt.subplots(1,2,figsize=(10,5.6),sharey=True,facecolor=SURF)
lo_all=[];hi_all=[]
for ax,(y,title) in zip(axes,panels):
    c=ES[(y,fe)]['coef']; yrs=[t for t in range(min(YRS),BASE+1)]
    est=[0.0 if t==BASE else c[f'conf_yr_{t}']['est'] for t in yrs]
    lo=[0.0 if t==BASE else c[f'conf_yr_{t}']['lo'] for t in yrs]; hi=[0.0 if t==BASE else c[f'conf_yr_{t}']['hi'] for t in yrs]
    lo_all+=lo; hi_all+=hi
    ax.axhline(0,color=INK2,lw=1,zorder=1)
    ax.axvspan(SH0-0.5,SH1+0.5,color=BAND,zorder=0,lw=0)
    for t,e,l,h in zip(yrs,est,lo,hi):
        if t==BASE: continue
        ax.plot([t,t],[l,h],color=BLUE,lw=2,solid_capstyle='round',zorder=2)
    xs=[t for t in yrs if t!=BASE]; es=[e for t,e in zip(yrs,est) if t!=BASE]
    ax.scatter(xs,es,s=42,color=BLUE,edgecolor=SURF,linewidth=1.5,zorder=3)
    ax.scatter([BASE],[0],s=42,facecolor=SURF,edgecolor=BLUE,linewidth=1.8,zorder=3)
    ax.set_title(title,loc='left',fontsize=11,color=INK,pad=8)
    ax.set_xticks(yrs); ax.set_xticklabels([str(t) for t in yrs],rotation=45,ha='right')
    ax.grid(axis='y',color=GRID,lw=0.8); ax.set_axisbelow(True)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.set_xlabel('Fiscal year')
    p=ES[(y,fe)]
    ax.text(0.0,-0.36,f"Pre-shock coefficients = 0: p = {p['pre']['p']:.3f};  equal: p = {p['preflat']['p']:.3f}\nShock-period coefficients = 0: p = {p['shock']['p']:.3f}\nPre-shock minus shock period: {p['contrast']['est']:.2f} (t = {p['contrast']['t']:.2f});  N = {p['N']:,}",transform=ax.transAxes,ha='left',va='top',fontsize=9,color=INK2)
axes[0].set_ylabel('Conflicted CIO x Year coefficient (pp)')
axes[0].annotate('FY2017 base\n(set to 0)',xy=(BASE,0),xytext=(BASE-1.6,max(hi_all)+0.05),fontsize=9,color=INK2,ha='center',arrowprops=dict(arrowstyle='-',color=INK2,lw=0.8))
for ax in axes: ax.text((SH0+SH1)/2,0.995,'Shock period\n(FY2009-2013)',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=9,color=INK2)
pad=0.25; axes[0].set_ylim(min(lo_all)-pad, max(max(hi_all),1.0)+0.75)
fig.suptitle('Event Study: Conflicted CIO Performance Around the Loglisci Shock',x=0.01,ha='left',fontsize=12,color=INK,y=0.975)
fig.text(0.01,0.035,"Coefficients on Conflicted CIO x fiscal-year indicators (FY2017 omitted) from the Table 5b specification with plan and year fixed effects; bars are 95% confidence intervals,\nstandard errors double clustered by plan and year. Endpoint bins for years before 2005 and after 2017 are in the regression but not plotted. Shading marks FY2009-2013 (shock2 = 1).",fontsize=8.5,color=INK2,ha='left',va='top')
fig.subplots_adjust(left=0.075,right=0.99,top=0.86,bottom=0.34,wspace=0.08)
out='/home/user/PensionData/referee_response/time_to_departure/eventstudy_shock_peer_bench_base2017'
fig.savefig(out+'.png',dpi=220,bbox_inches='tight',facecolor=SURF); fig.savefig(out+'.pdf',bbox_inches='tight',facecolor=SURF); print('saved')
