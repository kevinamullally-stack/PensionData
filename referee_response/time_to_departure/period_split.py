src=open('xsec_narrow.py').read().split("VERS=[")[0]; exec(src)
S['early']=(S.fy<=2008).astype(float)
U2=pd.read_pickle('comp_splits_res.pkl')
YS=[('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark')]
PV=[('narrow_fye','Narrow controls, fiscal-year-end FE',narrow('x'),'fye_id'),('paper_fy','Paper controls, year FE (published specification)',PAPER['underpaid'],'fy')]
PRES={v:{y:est2(y,'early',ctl,('ppd_id','fy'),fe) for y,_ in YS} for v,_,ctl,fe in PV}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
for v,vl,_,_ in PV:
    print(vl, ' || '.join(f"{y[:4]}: 2001-08 {fm(PRES[v][y]['a'])} vs 2009-20 {fm(PRES[v][y]['b'])} p={PRES[v][y]['d']['p']:.3f} N={PRES[v][y]['N']}" for y,_ in YS))
pd.to_pickle(PRES,'period_split_res.pkl')
