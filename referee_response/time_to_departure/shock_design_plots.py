import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D=pd.read_pickle('shock_tests.pkl'); R=D['R']; YS=D['YS']; BINS=D['BINS']; STARTS=D['STARTS']
BLUE='#2a78d6'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; SURF='#ffffff'; BAND='#f1f0ec'; GRAY='#9a9893'
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':10.5,'axes.edgecolor':INK2,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2})
OUT='/home/user/PensionData/referee_response/time_to_departure/'
FE='ppd_id + fy'
TITLES={'peer_adj_ret100':'A. Peer-adjusted return','b_AB':'B. Benchmark-adjusted return (updated benchmark)'}
def frame(ax,title):
    ax.axhline(0,color=INK2,lw=1,zorder=1); ax.grid(axis='y',color=GRID,lw=0.8); ax.set_axisbelow(True)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.set_title(title,loc='left',fontsize=11,color=INK,pad=8)
def bars(ax,xs,est,lo,hi,color=BLUE):
    for x,l,h in zip(xs,lo,hi): ax.plot([x,x],[l,h],color=color,lw=2,solid_capstyle='round',zorder=2)
    ax.scatter(xs,est,s=42,color=color,edgecolor=SURF,linewidth=1.5,zorder=3)
def finish(fig,title,note,fname,stats_by_ax,axes):
    for ax,txt in zip(axes,stats_by_ax): ax.text(0.0,-0.36,txt,transform=ax.transAxes,ha='left',va='top',fontsize=9,color=INK2)
    fig.suptitle(title,x=0.01,ha='left',fontsize=12,color=INK,y=0.975)
    fig.text(0.01,0.035,note,fontsize=8.5,color=INK2,ha='left',va='top')
    fig.subplots_adjust(left=0.075,right=0.99,top=0.86,bottom=0.34,wspace=0.08)
    fig.savefig(OUT+fname+'.png',dpi=220,bbox_inches='tight',facecolor=SURF); fig.savefig(OUT+fname+'.pdf',bbox_inches='tight',facecolor=SURF)
# ---- Figure 1: event study, FY2008 base ----
fig,axes=plt.subplots(1,2,figsize=(10,5.6),sharey=True,facecolor=SURF); sts=[]; lo_all=[]; hi_all=[]
for ax,(y,_) in zip(axes,YS):
    r=R[('es',y,FE)]; yrs=list(range(2005,2018))
    ax.axvspan(2008.5,2013.5,color=BAND,zorder=0,lw=0)
    xs=[t for t in yrs if t!=2008]; e=[r[f'es_{t}']['est'] for t in xs]; lo=[r[f'es_{t}']['lo'] for t in xs]; hi=[r[f'es_{t}']['hi'] for t in xs]
    lo_all+=lo; hi_all+=hi
    frame(ax,TITLES[y]); bars(ax,xs,e,lo,hi); ax.scatter([2008],[0],s=42,facecolor=SURF,edgecolor=BLUE,linewidth=1.8,zorder=3)
    ax.set_xticks(yrs); ax.set_xticklabels([str(t) for t in yrs],rotation=45,ha='right'); ax.set_xlabel('Fiscal year')
    ax.text(2011,0.995,'Shock period\n(FY2009-2013)',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=9,color=INK2)
    sts.append(f"Pre-shock leads = 0: p = {r['pre']['p']:.3f}\nShock-period coefs = 0: p = {r['win']['p']:.3f}; mean {r['win_mean']['est']:.2f} (t = {r['win_mean']['t']:.2f})\nPost mean minus shock mean: {r['return']['est']:.2f} (t = {r['return']['t']:.2f})\nN = {r['N']:,}")
axes[0].set_ylabel('Change in the effect of conflict\nrelative to FY2008 (pp)')
axes[0].annotate('FY2008 base',xy=(2008,0),xytext=(2006.4,max(hi_all)+0.15),fontsize=9,color=INK2,ha='center',arrowprops=dict(arrowstyle='-',color=INK2,lw=0.8))
axes[0].set_ylim(min(lo_all)-0.3,max(hi_all)+0.8)
finish(fig,'Event Study Around the Loglisci Shock (FY2008 Base)',
 "Coefficients on Conflicted CIO x fiscal-year indicators relative to FY2008 (the last fiscal year before the Shock Period), from regressions that also include Conflicted CIO, the Table 5b controls,\nand plan and year fixed effects; bars are 95% confidence intervals, standard errors double clustered by plan and year. Endpoint bins for years before 2005 and after 2017 are estimated but not plotted.",
 'shock_eventstudy_fy2008',sts,axes); plt.close(fig)
# ---- Figure 2: two-year bins, reference FY2007-08 ----
LAB={'b0102':'2001-02','b0304':'2003-04','b0506':'2005-06','ref':'2007-08','b0910':'2009-10','b1113':'2011-13','b1415':'2014-15','b1617':'2016-17','b1820':'2018-20'}
order=['b0102','b0304','b0506','ref','b0910','b1113','b1415','b1617','b1820']
fig,axes=plt.subplots(1,2,figsize=(10,5.6),sharey=True,facecolor=SURF); sts=[]; lo_all=[]; hi_all=[]
for ax,(y,_) in zip(axes,YS):
    r=R[('bins',y,FE)]; xs=list(range(len(order)))
    ax.axvspan(3.5,5.5,color=BAND,zorder=0,lw=0)
    pts=[(i,k) for i,k in enumerate(order) if k!='ref']
    e=[r[k]['est'] for _,k in pts]; lo=[r[k]['lo'] for _,k in pts]; hi=[r[k]['hi'] for _,k in pts]; lo_all+=lo; hi_all+=hi
    frame(ax,TITLES[y]); bars(ax,[i for i,_ in pts],e,lo,hi); ax.scatter([3],[0],s=42,facecolor=SURF,edgecolor=BLUE,linewidth=1.8,zorder=3)
    ax.set_xticks(xs); ax.set_xticklabels([LAB[k] for k in order],rotation=45,ha='right'); ax.set_xlabel('Fiscal years')
    ax.text(4.5,0.995,'Shock period',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=9,color=INK2)
    sts.append(f"Pre-shock bins = 0: p = {r['pre']['p']:.3f}\nShock-period bins = 0: p = {r['win']['p']:.3f}\nPost-period bins = 0: p = {r['post']['p']:.3f};  N = {r['N']:,}")
axes[0].set_ylabel('Change in the effect of conflict\nrelative to FY2007-08 (pp)')
axes[0].set_ylim(min(lo_all)-0.3,max(hi_all)+0.6)
finish(fig,'Event Study Around the Loglisci Shock (Two-Year Bins, FY2007-08 Base)',
 "Coefficients on Conflicted CIO x period indicators relative to FY2007-08, from regressions that also include Conflicted CIO, the Table 5b controls, and plan and year fixed effects;\nbars are 95% confidence intervals, standard errors double clustered by plan and year. The shock period is split into FY2009-10 and FY2011-13.",
 'shock_eventstudy_bins',sts,axes); plt.close(fig)
# ---- Figure 3: rolling placebo windows ----
fig,axes=plt.subplots(1,2,figsize=(10,5.6),sharey=True,facecolor=SURF); sts=[]; lo_all=[]; hi_all=[]
for ax,(y,_) in zip(axes,YS):
    frame(ax,TITLES[y])
    rr=[R[('roll',s,y,FE)]['cxw'] for s in STARTS]
    lo_all+=[x['lo'] for x in rr]; hi_all+=[x['hi'] for x in rr]
    oth=[(s,x) for s,x in zip(STARTS,rr) if s!=2009]; tru=[(s,x) for s,x in zip(STARTS,rr) if s==2009]
    bars(ax,[s for s,_ in oth],[x['est'] for _,x in oth],[x['lo'] for _,x in oth],[x['hi'] for _,x in oth],color=GRAY)
    bars(ax,[s for s,_ in tru],[x['est'] for _,x in tru],[x['lo'] for _,x in tru],[x['hi'] for _,x in tru],color=BLUE)
    ax.set_xticks(STARTS); ax.set_xticklabels([f"{s}-{str(s+4)[2:]}" for s in STARTS],rotation=45,ha='right'); ax.set_xlabel('Five-year window (fiscal years)')
    rank=1+sum(x['est']>tru[0][1]['est'] for _,x in oth)
    nonov=[x['est'] for s,x in oth if s+4<2009 or s>2013]
    sts.append(f"Actual window (FY2009-13): {tru[0][1]['est']:.2f} (t = {tru[0][1]['t']:.2f}); rank {rank} of {len(STARTS)}\nNon-overlapping placebo windows: {min(nonov):.2f} to {max(nonov):.2f}")
    ax.annotate('Actual shock\nwindow',xy=(2009,tru[0][1]['hi']),xytext=(2011.6,tru[0][1]['hi']+0.35),fontsize=9,color=INK2,ha='center',arrowprops=dict(arrowstyle='-',color=INK2,lw=0.8))
axes[0].set_ylabel('Conflicted CIO x Window coefficient (pp)')
axes[0].set_ylim(min(lo_all)-0.3,max(hi_all)+0.9)
finish(fig,'Placebo Windows: Conflicted CIO x Five-Year Window',
 "Each point re-estimates Table VIII (plan and year fixed effects) with the Shock Period replaced by a five-year window of fiscal years starting in the year shown; bars are 95% confidence intervals,\nstandard errors double clustered by plan and year. Windows overlapping FY2009-2013 partly contain the actual shock period.",
 'shock_placebo_windows',sts,axes); plt.close(fig)
print('saved')
