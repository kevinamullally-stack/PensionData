exec(open('table3_conflicted_halves_fye1.py').read().split("RES={(v,y)")[0])     # S (Table III sample) with halves, VERS, controls
from scipy import stats
S_full=S.copy()
PER={'full':('Full sample (FY2002-2020)',S_full.fy.notna()),'pre2009':('Through FY2008',S_full.fy<=2008),'ex0914':('Excluding FY2009-2014',~S_full.fy.between(2009,2014))}
RP=pd.read_pickle('table3_conflicted_halves_preshock.pkl')['RES']; RF=pd.read_pickle('table3_conflicted_halves_fye1.pkl')['RES']
def res(per,y): return RF[('paper',y)] if per=='full' else RP[(per,'paper',y)]
CTL=C1+C2+C3+C4+C5
OUT={}
for per,(lab,mask) in PER.items():
    for y,yl in YS:
        d=S_full[mask].dropna(subset=[y]+CTL)
        d=d[d.fye_id.map(d.fye_id.value_counts())>1]                       # column 1 estimation sample (FYE FE)
        c=d[d.conf_pen_vendor==1]
        sp=c.groupby('cp').agg(n=('fy','size'),h=('second','nunique'),ten=('ten_dep','first'),first_fy=('fy','min'),last_fy=('fy','max'))
        cio=c.groupby('cio').agg(n=('fy','size'),h=('second','nunique'))
        regs=res(per,y); G=[r['G'] for r in regs]
        se=[r['diff'][1] for r in regs]; mde=[(stats.t.ppf(0.975,g-1)+stats.t.ppf(0.80,g-1))*s for s,g in zip(se,G)]
        OUT[(per,y)]=dict(label=lab,N=len(d),plans=d.ppd_id.nunique(),years=d.fy.nunique(),fy_min=int(d.fy.min()),fy_max=int(d.fy.max()),
            conf=len(c),conf_share=len(c)/len(d),h1=int((c.second==0).sum()),h2=int((c.second==1).sum()),
            conf_cios=c.cio.nunique(),conf_spells=c.cp.nunique(),conf_plans=c.ppd_id.nunique(),
            cios_both=int((cio.h==2).sum()),spells_both=int((sp.h==2).sum()),
            py_per_cio=cio.n.mean(),py_per_spell=sp.n.mean(),py_per_spell_med=sp.n.median(),
            ten_dep=sp.ten.mean(),ten_dep_med=sp.ten.median(),ten_mean=c.cio_tenure.mean(),ten_h1=c.loc[c.second==0,'cio_tenure'].mean(),ten_h2=c.loc[c.second==1,'cio_tenure'].mean(),
            N_cols=[r['N'] for r in regs],Gy=[r['Gy'] for r in regs],Gp=[r['Gp'] for r in regs],se=se,mde=mde,
            diff=[r['diff'][0] for r in regs],h1coef=regs[0]['est']['h1'][0],h2coef=regs[0]['est']['h2'][0],n4=regs[3]['N'],sp4=regs[3]['ncio'])
for per,(lab,_) in PER.items():
    for y,yl in YS:
        o=OUT[(per,y)]
        print(f"\n### {lab} | {yl}")
        print(f"  plan-years {o['N']} ({o['fy_min']}-{o['fy_max']}, {o['years']} fiscal years, {o['plans']} plans) | conflicted {o['conf']} ({o['conf_share']:.1%}): first {o['h1']}, second {o['h2']}")
        print(f"  conflicted CIOs {o['conf_cios']}, CIO-plan tenures {o['conf_spells']}, plans {o['conf_plans']} | CIOs observed in both halves {o['cios_both']} (tenures {o['spells_both']})")
        print(f"  conflicted plan-years per CIO {o['py_per_cio']:.1f}, per tenure {o['py_per_spell']:.1f} (median {o['py_per_spell_med']:.0f}) | tenure at departure mean {o['ten_dep']:.1f} (median {o['ten_dep_med']:.0f}) | mean tenure in sample {o['ten_mean']:.1f} (first half {o['ten_h1']:.1f}, second {o['ten_h2']:.1f})")
        print(f"  cols N {o['N_cols']} | year clusters {o['Gy']} | SE(second-first) {[round(s,3) for s in o['se']]} | MDE80 {[round(m,2) for m in o['mde']]} | est diff {[round(x,2) for x in o['diff']]} | col4 N {o['n4']} tenures/CIOs {o['sp4']}")
pd.to_pickle(OUT,'preshock_halves_power.pkl')
