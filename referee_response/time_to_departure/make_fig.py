"""Event-time figure. Run after ttd_analysis.py (needs df_built.pkl)."""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
OUT = os.path.dirname(os.path.abspath(__file__))
df = pd.read_pickle(os.path.join(OUT,'df_built.pkl'))
CTRL = 'size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB + sib1 + cio_age + cio_tenure + prior_private_exp + Elite_inst'
CTRL_SPELL = 'size + ActFundedRatio_GASB + InvestmentReturnAssumption_GASB'
BINS = ['m5','m4','m3','m2','m1','p0']; XL = ['≤ −5','−4','−3','−2','−1','0\n(exit yr)']
BLUE, ORANGE = '#2a78d6', '#eb6834'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'
def est(y, fe, ctrl, rel):
    use = BINS[1:] if rel else BINS
    rhs = ' + '.join([f'c_{b}' for b in use]+[f'o_{b}' for b in use]) + ' + ' + ctrl
    m = pf.feols(f'{y} ~ {rhs} | {fe}', data=df, vcov={'CRV1':'ppd_id'})
    tcrit = stats.t.ppf(0.975, m._G[0]-1)
    out = {}
    for g in ['c','o']:
        b = [0.0] + [m.coef()[f'{g}_{x}'] for x in use] if rel else [m.coef()[f'{g}_{x}'] for x in use]
        s = [0.0] + [m.se()[f'{g}_{x}'] for x in use] if rel else [m.se()[f'{g}_{x}'] for x in use]
        out[g] = (np.array(b), np.array(s)*tcrit)
    return out, m._N
panels = [('ret100','ppd_id + fy',CTRL,False,'Peer-adjusted return','A. Pooled: plan + year FE (level vs. non-departing CIO-years)'),
          ('bret100','ppd_id + fy',CTRL,False,'Benchmark-adjusted return','B. Pooled: plan + year FE'),
          ('ret100','spell + fy',CTRL_SPELL,True,'Peer-adjusted return','C. Within CIO: CIO-spell + year FE (relative to own ≤ −5 years)'),
          ('bret100','spell + fy',CTRL_SPELL,True,'Benchmark-adjusted return','D. Within CIO: CIO-spell + year FE')]
fig, axes = plt.subplots(2, 2, figsize=(11, 7.6), sharex=True)
x = np.arange(6)
for ax, (y, fe, ctrl, rel, ylab, title) in zip(axes.flat, panels):
    r, N = est(y, fe, ctrl, rel)
    for g, col, lab, dx in [('c',BLUE,'Conflicted CIO (leaves for vendor)',-0.08),('o',ORANGE,'Other observed departure',0.08)]:
        b, ci = r[g]
        ax.plot(x+dx, b, color=col, lw=1.6, zorder=2)
        ax.errorbar(x+dx, b, yerr=ci, fmt='o', color=col, ms=6, mfc='white', mew=1.6, capsize=3, lw=1.2, label=lab, zorder=3)
    ax.axhline(0, color=INK2, lw=0.8, ls='--', zorder=1)
    ax.set_title(f"{title}   N = {N:,}", fontsize=9.5, loc='left', color=INK)
    ax.set_ylabel(f"{ylab} (pp)", fontsize=9, color=INK)
    ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    for s in ['left','bottom']: ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8.5)
    ax.set_xticks(x); ax.set_xticklabels(XL)
for ax in axes[1]: ax.set_xlabel('Fiscal years to CIO departure', fontsize=9, color=INK)
h, l = axes[0,0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.005))
fig.suptitle('Performance profile over the run-up to CIO departure (95% CIs, SE clustered by plan)', fontsize=11, color=INK, x=0.02, ha='left')
fig.text(0.02, 0.935, 'Pooled panels include baseline controls; within-CIO panels drop CIO-level controls absorbed by the spell effects.', fontsize=8.3, color=INK2)
fig.tight_layout(rect=[0,0.05,1,0.93])
fig.savefig(os.path.join(OUT,'fig_event_time.png'), dpi=200, facecolor='white'); fig.savefig(os.path.join(OUT,'fig_event_time.pdf'), facecolor='white')
print('saved')
