exec(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'xsec_setup.py')).read())
YS = [('peer_adj_ret100','Peer-adjusted return (paper)'),('bench_adj_ret_pct','Benchmark-adjusted, original benchmark'),('b_AB','Benchmark-adjusted, updated benchmark'),
      ('b_rep','Updated, reported benchmarks only'),('b_all','Updated, reported + all inferred'),('b_docAB','Updated, document-matched return'),('b_AB_ok','Updated, PPD and document returns agree within 0.5 pp')]
RES = {}
for key,sv,ctrls,cl,labs,tab in SPLITS:
    RES[key] = {y: est(y, sv, ctrls, cl) for y,_ in YS}
def star(p): return '' if np.isnan(p) else '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def f(r): return f"{r['est']:7.3f}{star(r['p']):3s}({r['t']:5.2f})"
out=[]
def P(*a): s=' '.join(str(x) for x in a); print(s); out.append(s)
P("# Cross-sectional tests (Tables V-VII) with the updated benchmark. Do-file specifications; year FE; SE double clustered by plan and year (plan and fiscal-year-end date for the financial-center split); t in parentheses.")
for key,sv,ctrls,cl,(l1,l0),tab in SPLITS:
    P(f"\n## {tab}: {l1} vs {l0}")
    P(f"{'dependent variable':56s} {l1+' x Conf':26s} {l0+' x Conf':26s} {'p(equal)':9s} N")
    for y,yl in YS:
        r=RES[key][y]; P(f"{yl:56s} {f(r['a']):26s} {f(r['b']):26s} {r['d']['p']:<9.3f} {r['N']}")
open('/home/user/PensionData/referee_response/time_to_departure/results_xsec_updated_benchmark.md','w').write('\n'.join(out))
pd.to_pickle(dict(RES=RES, YS=YS, SPLITS=[(k,sv,cl,labs,tab) for k,sv,c,cl,labs,tab in SPLITS]), 'xsec_newbench_res.pkl')
