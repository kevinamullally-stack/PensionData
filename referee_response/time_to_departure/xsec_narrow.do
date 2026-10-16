**** Cross-sectional splits with narrow controls; compensation definitions; period split ****
* Regenerates xsec_narrow_controls.xlsx.
*   Tables V-VII (split method: controls interacted with the group indicator, test of equal
*   Conflicted coefficients) with narrow controls (size, lagged funding, lagged allocations) and
*   fiscal-year-end date FE, plus four comparison specifications; seven definitions of high vs. low
*   CIO pay; and a 2001-2008 vs. 2009-2020 split.
*
* Run AFTER updated_benchmark_tables.do, which creates bench_adj_upd.

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* --- split indicators (missing CIO age / funding coded missing) and spell identifiers ---------
capture drop young highrate highfund insamp pay_spell negfy early
generate young = (cio_age<=46) if !missing(cio_age)
generate highrate = (InvestmentReturnAssumption_GASB>0.08) if !missing(InvestmentReturnAssumption_GASB)
generate highfund = (ActFundedRatio_GASB>=92) if !missing(ActFundedRatio_GASB)
generate byte insamp = (cio_dum==1 & fy<=2020 & curr1==0)
egen pay_spell = group(cio ppd_id)
generate negfy = -fy
generate early = (fy<=2008)

* --- CIO pay definitions: 1 = lower-paid group ------------------------------------------------
* Computed over all plan-years with reported CIO_TotalComp, then filled within the CIO's spell at
* the plan (nearest earlier reported year carried forward, first reported year carried back).
capture drop pay_ok c_fixed c_annual c_real c_size c_top3 c_top4 c_bot3 cpi real_pay lc_pay lc_res _med _rmed _p66_67 _p75 _p33_33
generate byte pay_ok = !missing(CIO_TotalComp) & inrange(fy,2001,2020)
* (1) the paper's cutoff: pooled 2009-2014 median (224,578)
quietly summarize CIO_TotalComp if pay_ok & inrange(fy,2009,2014), detail
generate c_fixed = (CIO_TotalComp < r(p50)) if pay_ok
* (2) median of the same fiscal year
bysort fy: egen _med = median(cond(pay_ok, CIO_TotalComp, .))
generate c_annual = (CIO_TotalComp < _med) if pay_ok
* (3) pooled median of inflation-adjusted pay (CPI-U annual average, BLS series CUUR0000SA0, 2020 dollars)
generate cpi = .
foreach pair in "2001 177.1" "2002 179.9" "2003 184.0" "2004 188.9" "2005 195.3" "2006 201.6" "2007 207.342" "2008 215.303" "2009 214.537" "2010 218.056" ///
                "2011 224.939" "2012 229.594" "2013 232.957" "2014 236.736" "2015 237.017" "2016 240.007" "2017 245.120" "2018 251.107" "2019 255.657" "2020 258.811" {
	tokenize `pair'
	replace cpi = `2' if fy==`1'
}
generate real_pay = CIO_TotalComp*258.811/cpi if pay_ok
quietly summarize real_pay if pay_ok, detail
generate c_real = (real_pay < r(p50)) if pay_ok
label variable c_real "Underpaid: real CIO pay below pooled median (2020 dollars)"
* (4) pay given plan size: residual of log pay on size and fiscal-year indicators, below that year's median
generate lc_pay = ln(CIO_TotalComp) if pay_ok
quietly regress lc_pay size i.fy if pay_ok
predict lc_res if e(sample), residuals
bysort fy: egen _rmed = median(lc_res)
generate c_size = (lc_res < _rmed) if !missing(lc_res)
* (5)-(7) cutoffs within each fiscal year
bysort fy: egen _p66_67 = pctile(cond(pay_ok, CIO_TotalComp, .)), p(66.67)
bysort fy: egen _p75    = pctile(cond(pay_ok, CIO_TotalComp, .)), p(75)
bysort fy: egen _p33_33 = pctile(cond(pay_ok, CIO_TotalComp, .)), p(33.33)
generate c_top3 = (CIO_TotalComp < _p66_67) if pay_ok      // 0 = top third of pay that year
generate c_top4 = (CIO_TotalComp < _p75)    if pay_ok      // 0 = top quarter of pay that year
generate c_bot3 = (CIO_TotalComp < _p33_33) if pay_ok      // 1 = bottom third of pay that year
foreach v in c_fixed c_annual c_real c_size c_top3 c_top4 c_bot3 {
	replace `v' = . if !insamp
	bysort insamp pay_spell (fy):    replace `v' = `v'[_n-1] if missing(`v') & insamp & !missing(pay_spell) & _n>1
	bysort insamp pay_spell (negfy): replace `v' = `v'[_n-1] if missing(`v') & insamp & !missing(pay_spell) & _n>1
}

* --- helper: one split regression ----------------------------------------------------------------
* splitreg y s, controls() absorb() cluster() out() mode(replace|append) [need() label()]
* need(): also require these variables to be non-missing (used to hold the paper-controls sample)
capture program drop splitreg
program define splitreg
	syntax varlist(min=2 max=2), CONTROLS(varlist) ABSORB(varname) CLUSTER(varlist) OUT(string) MODE(string) [NEED(varlist) LABEL(string)]
	tokenize `varlist'
	local y `1'
	local s `2'
	capture drop s1_*
	capture drop s0_*
	quietly {
		generate s1_conf = `s'*conf_pen_vendor
		generate s0_conf = (1-`s')*conf_pen_vendor
		local ints
		foreach var of local controls {
			generate s1_`var' = `s'*`var'
			generate s0_`var' = (1-`s')*`var'
			local ints `ints' s1_`var' s0_`var'
		}
	}
	label variable s1_conf "Group 1 x Conflicted CIO"
	label variable s0_conf "Group 0 x Conflicted CIO"
	local cond cio_dum==1 & curr1==0 & fy<=2020
	if "`need'"!="" {
		tempvar nm
		egen `nm' = rowmiss(`need')
		local cond `cond' & `nm'==0
	}
	reghdfe `y' s1_conf s0_conf `s' `ints' if `cond', absorb(`absorb') vce(cluster `cluster')
	test s1_conf = s0_conf
	local p1 = r(p)
	outreg2 using `out', excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(s1_conf s0_conf) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Dep. var., `y', Split, `s', Spec, `label') `mode'
	drop s1_* s0_*
end

* --- control lists ------------------------------------------------------------------------------
local alloc l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
local narrow size l_ActFundedRatio_GASB `alloc'
local narrow_highfund size `alloc'                      // the paper's funding block omits lagged funding
local c1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
local ctl_underpaid         `c1' `alloc' fincenter1 l_log_cio_tenure l_log_cio_age l_sib1 wstate_political
local ctl_c_annual          `ctl_underpaid'
local ctl_young             `c1' `alloc' fincenter1 l_sib1 wstate_political
local ctl_prior_private_exp `c1' `alloc' fincenter1 l_log_cio_tenure l_sib1 wstate_political
local ctl_fincenter1        `c1' `alloc' l_log_cio_tenure l_sib1 wstate_political
local ctl_highrate          `c1' `alloc' fincenter1 l_log_cio_tenure l_sib1 wstate_political
local ctl_highfund          l_investmentreturn_1yr size `alloc' fincenter1 l_log_cio_tenure

* =====================================================================================
* 1. Tables V-VII and the specification comparison (c_annual = Table V, Panel C)
*    Specifications, in order: narrow fye1 (Tables V-VII sheets), narrow fy, narrow fye1 on the
*    paper-controls sample, paper controls fye1, paper controls fy (published)
* =====================================================================================
foreach s in underpaid c_annual young prior_private_exp fincenter1 highrate highfund {
	local cl ppd_id fy
	if "`s'"=="fincenter1" local cl ppd_id fye1
	local nar `narrow'
	if "`s'"=="highfund" local nar `narrow_highfund'
	local pap `ctl_`s''
	local mode replace
	foreach y in peer_adj_ret bench_adj_upd {
		splitreg `y' `s', controls(`nar') absorb(fye1) cluster(`cl') out(xsec_narrow_`s') mode(`mode') label(narrow fye1)
		local mode append
		splitreg `y' `s', controls(`nar') absorb(fy)   cluster(`cl') out(xsec_narrow_`s') mode(append) label(narrow fy)
		splitreg `y' `s', controls(`nar') absorb(fye1) cluster(`cl') out(xsec_narrow_`s') mode(append) label(narrow fye1 paper sample) need(`pap')
		splitreg `y' `s', controls(`pap') absorb(fye1) cluster(`cl') out(xsec_narrow_`s') mode(append) label(paper fye1)
		splitreg `y' `s', controls(`pap') absorb(fy)   cluster(`cl') out(xsec_narrow_`s') mode(append) label(paper fy)
	}
}

* =====================================================================================
* 2. Compensation splits (group 1 = lower-paid)
* =====================================================================================
foreach s in c_fixed c_annual c_real c_size c_top3 c_top4 c_bot3 {
	local mode replace
	foreach y in peer_adj_ret bench_adj_upd {
		splitreg `y' `s', controls(`narrow')        absorb(fye1) cluster(ppd_id fy) out(xsec_comp_`s') mode(`mode') label(narrow fye1)
		local mode append
		splitreg `y' `s', controls(`ctl_underpaid') absorb(fy)   cluster(ppd_id fy) out(xsec_comp_`s') mode(append) label(paper fy)
	}
}
tabulate fy c_real if insamp, row nofreq

* =====================================================================================
* 3. Period split: 2001-2008 (group 1) vs. 2009-2020
* =====================================================================================
local mode replace
foreach y in peer_adj_ret bench_adj_upd {
	splitreg `y' early, controls(`narrow')        absorb(fye1) cluster(ppd_id fy) out(xsec_period_split) mode(`mode') label(narrow fye1)
	local mode append
	splitreg `y' early, controls(`ctl_underpaid') absorb(fy)   cluster(ppd_id fy) out(xsec_period_split) mode(append) label(paper fy)
}

* =====================================================================================
* 4. Log pay x time: the Log CIO Total Comp. interaction (all controls + fye1 FE) with the effect
*    of conflict allowed to vary over time. Needs the contint program and log_comp from
*    xsec_interactions.do.
* =====================================================================================
capture program list contint
if _rc {
	display as error "run xsec_interactions.do first (it defines contint and log_comp)"
	exit 111
}
capture drop trend
capture drop yd*
generate trend = fy
quietly tabulate fy if insamp, generate(yd)
local yd
foreach v of varlist yd* {
	quietly summarize fy if `v'==1
	if r(min)>2001 local yd `yd' `v'          // 2001 is the omitted year
}
local full l_investmentreturn_1yr size l_ActFundedRatio_GASB `alloc' fincenter1 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst l_sib1 wstate_political
foreach y in peer_adj_ret bench_adj_upd {
	global name1 xsecint_logpay_time_`y'
	contint `y' log_comp, controls(`full') out($name1) mode(replace) label(1 base)
	contint `y' log_comp, controls(`full') out($name1) mode(append)  label(2 conf x 2001-08) extra(early)
	contint `y' log_comp, controls(`full') out($name1) mode(append)  label(3 conf x trend) extra(trend)
	contint `y' log_comp, controls(`full') out($name1) mode(append)  label(4 conf x year indicators) extra(`yd')
}
**** End narrow controls ****
