exec(open('xsec_setup_v2.py').read())
U=pd.read_pickle('underpaid_check.pkl')['S'][['ppd_id','fy','up_rc','up_rc_raw']]
S=S.merge(U,on=['ppd_id','fy'],how='left',validate='1:1')
k,sv,ctrls,cl,labs,tab=SPLITS[0]
SPL={}
for v,l in [('underpaid','Underpaid as in the paper (fixed $224,578 cutoff)'),('up_rc','Annual-median Underpaid, filled within spell'),('up_rc_raw','Annual-median Underpaid, reported years only')]:
    for y in ['peer_adj_ret100','b_AB']:
        r=est(y,v,ctrls,cl); SPL[(v,y)]=r
        print(f"{l[:50]:50s} {y[:6]:6s} underpaid x conf {r['a']['est']:6.3f} ({r['a']['t']:5.2f}) | paid x conf {r['b']['est']:6.3f} ({r['b']['t']:5.2f}) | diff {r['d']['est']:6.3f} p={r['d']['p']:.3f} | N {r['N']}")
pd.to_pickle(SPL,'underpaid_split_check.pkl')
