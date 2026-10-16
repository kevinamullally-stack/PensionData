src=open('interact_comp.py').read().split("YS=[")[0]
src=src.replace("ext={e:lc({'conf_'+e:1}) for e in extra},","ext={e:lc({'conf_'+e:1}) for e in extra if 'conf_'+e in names}, dropped=[e for e in extra if 'conf_'+e not in names],")
exec(src)     # S with log_comp, FULL, run(y, xv, extra, drop, need)
S['early']=(S.fy<=2008).astype(float)
S['trend']=S.fy.astype(float)
YD=[f'yd{y}' for y in range(2002,2021)]
for y,c in zip(range(2002,2021),YD): S[c]=(S.fy==y).astype(float)
YS=[('peer_adj_ret100','Peer-adjusted'),('b_AB','Benchmark-adjusted, updated benchmark')]
V=[('base','Log pay (as in the Interactions sheet)',()),
   ('early','+ Conflicted x 2001-2008 indicator',('early',)),
   ('trend','+ Conflicted x linear year trend',('trend',)),
   ('years','+ Conflicted x fiscal-year indicators',tuple(YD))]
CT={v:{y:run(y,'log_comp',ex) for y,_ in YS} for v,_,ex in V}
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}({r['t']:5.2f})"
for v,vl,ex in V:
    print(f"{vl:44s}", ' || '.join(f"{y[:4]}: conf x logpay {fm(CT[v][y]['confX'])} | conf@mean {fm(CT[v][y]['conf'])}" + (f" | conf x early {fm(CT[v][y]['ext']['early'])}" if v=='early' else '') + f" N {CT[v][y]['N']} dropped {CT[v][y]['dropped']}" for y,_ in YS))
pd.to_pickle(dict(CT=CT,V=[(a,b) for a,b,_ in V]),'comp_time_check.pkl')
