src=open('shock_tests.py').read().split("FES=[('fy'")[0]; exec(src)     # S, CTL, YS, fit()
FES2=[('fye_id','Fiscal-year-end FE'),('ppd_id + fye_id','Plan and fiscal-year-end FE')]
# periods: (coefficient name or None for the omitted base, fiscal years covered in the 2002-2020 sample, group)
SINGLE=[('es_pre',[2002,2003,2004],'pre')]+[(f'es_{t}',[t],'pre') for t in (2005,2006,2007)]+[(None,[2008],'pre')] \
      +[(f'es_{t}',[t],'shock') for t in range(2009,2014)]+[(f'es_{t}',[t],'post') for t in range(2014,2018)]+[('es_post',[2018,2019,2020],'post')]
BINP=[('b0102',[2002],'pre'),('b0304',[2003,2004],'pre'),('b0506',[2005,2006],'pre'),(None,[2007,2008],'pre'),
      ('b0910',[2009,2010],'shock'),('b1113',[2011,2012,2013],'shock'),('b1415',[2014,2015],'post'),('b1617',[2016,2017],'post'),('b1820',[2018,2019,2020],'post')]
S['es_pre']=S.conf*(S.fy<2005); S['es_post']=S.conf*(S.fy>2017)
for t in [t for t in range(2005,2018) if t!=2008]: S[f'es_{t}']=S.conf*(S.fy==t)
for nm,a,z in [('b0102',2001,2002),('b0304',2003,2004),('b0506',2005,2006),('b0910',2009,2010),('b1113',2011,2013),('b1415',2014,2015),('b1617',2016,2017),('b1820',2018,2020)]:
    S[nm]=S.conf*S.fy.between(a,z)
def means(periods, groups):
    """year-weighted mean of the event coefficients over the periods in `groups` (base counts as 0)"""
    ps=[p for p in periods if p[2] in groups]; W=sum(len(p[1]) for p in ps)
    return {p[0]:len(p[1])/W for p in ps if p[0] is not None}
def sub(a,b):
    out=dict(a)
    for k,v in b.items(): out[k]=out.get(k,0)-v
    return out
def combos(periods):
    names=[p[0] for p in periods if p[0]]
    c={n:{n:1} for n in names}; c['conf']={'conf':1}
    for g,grp in [('shock',['shock']),('non',['pre','post']),('pre',['pre']),('post',['post'])]:
        c[f'm_{g}']=means(periods,grp)                      # mean relative to the base period
        c[f'lvl_{g}']={**c[f'm_{g}'],'conf':1}               # average effect of conflict in those years
    c['d_non']=sub(c['m_shock'],c['m_non']); c['d_pre']=sub(c['m_shock'],c['m_pre']); c['d_post']=sub(c['m_shock'],c['m_post'])
    return c
RES={}
for y,_ in YS:
    for fe,_ in FES2:
        RES[('single',y,fe)]=fit(y,['conf']+[p[0] for p in SINGLE if p[0]]+CTL,fe,combos(SINGLE))
        RES[('bins',y,fe)]=fit(y,['conf']+[p[0] for p in BINP if p[0]]+CTL,fe,combos(BINP))
def st(p): return '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''
def fm(r): return f"{r['est']:6.3f}{st(r['p']):3s}(t={r['t']:5.2f}, p={r['p']:.3f})"
for es,lab in [('single','Single years, FY2008 base'),('bins','Two-year bins, FY2007-08 base')]:
    print(f"\n######## {lab}")
    for y,yl in YS:
        for fe,fl in FES2:
            r=RES[(es,y,fe)]
            print(f"{yl[:22]:22s} {fl:28s} shock yrs {r['lvl_shock']['est']:6.3f} | non-shock yrs {r['lvl_non']['est']:6.3f} | diff {fm(r['d_non'])} || pre {r['lvl_pre']['est']:6.3f} post {r['lvl_post']['est']:6.3f} | shock-pre {fm(r['d_pre'])} | shock-post {fm(r['d_post'])} | N {r['N']}")
pd.to_pickle(dict(RES=RES,YS=YS,FES2=FES2,SINGLE=SINGLE,BINP=BINP),'shock_es_fye.pkl')
