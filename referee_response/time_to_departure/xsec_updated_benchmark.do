**** Tables V-VII (cross-sectional tests) with the updated policy benchmark ****
* Run AFTER table3_updated_benchmark.do, which creates bench_adj_upd (PPD return minus the updated
* benchmark) and bench_adj_upd_doc (document-matched). Uses the main do-file's scaling, lags and sample.
* Each split re-estimates the do-file's specification for three dependent variables:
*   peer_adj_ret (paper), bench_adj_ret_pct (original benchmark), bench_adj_upd (updated benchmark).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run table3_updated_benchmark.do first (it creates bench_adj_upd)"
	exit 111
}

* --- split indicators, exactly as in the main do-file ---------------------------------------
capture drop young highrate highfund
generate young=1 if cio_age<=46
replace  young=0 if cio_age>46
generate highrate=1 if InvestmentReturnAssumption_GASB>0.08 & !missing(InvestmentReturnAssumption_GASB)
replace  highrate=0 if InvestmentReturnAssumption_GASB<=0.08 & !missing(InvestmentReturnAssumption_GASB)
generate highfund=1 if ActFundedRatio_GASB>=92 & !missing(InvestmentReturnAssumption_GASB)
replace  highfund=0 if ActFundedRatio_GASB<92 & !missing(InvestmentReturnAssumption_GASB)

* --- control lists: the globals in effect in each block of the main do-file ------------------
local c1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
local c2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
local ctl_underpaid         `c1' `c2' fincenter1 l_log_cio_tenure l_log_cio_age l_sib1 wstate_political
local ctl_young             `c1' `c2' fincenter1 l_sib1 wstate_political
local ctl_prior_private_exp `c1' `c2' fincenter1 l_log_cio_tenure l_sib1 wstate_political
local ctl_fincenter1        `c1' `c2' l_log_cio_tenure l_sib1 wstate_political
local ctl_highrate          `c1' `c2' fincenter1 l_log_cio_tenure l_sib1 wstate_political
local ctl_highfund          l_investmentreturn_1yr size `c2' fincenter1 l_log_cio_tenure

foreach s in underpaid young prior_private_exp fincenter1 highrate highfund {
	* the main do-file clusters the financial-center test by plan and fiscal-year-end date
	local cl ppd_id fy
	if "`s'"=="fincenter1" local cl ppd_id fye1

	capture drop s1_* s0_*
	generate s1_conf = `s'*conf_pen_vendor
	generate s0_conf = (1-`s')*conf_pen_vendor
	local ints
	foreach var of local ctl_`s' {
		generate s1_`var' = `s'*`var'
		generate s0_`var' = (1-`s')*`var'
		local ints `ints' s1_`var' s0_`var'
	}
	label variable s1_conf "`s'=1 x Conflicted CIO"
	label variable s0_conf "`s'=0 x Conflicted CIO"

	global name1 xsec_`s'
	local first 1
	foreach y in peer_adj_ret bench_adj_ret_pct bench_adj_upd {
		reghdfe `y' s1_conf s0_conf `s' `ints' if cio_dum==1 & curr1==0 & fy<=2020, absorb(fy) vce(cluster `cl')
		test s1_conf = s0_conf
		local p1 = r(p)
		if `first' outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(s1_conf s0_conf) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Dep. var., `y') replace
		else      outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(s1_conf s0_conf) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Dep. var., `y') append
		local first 0
	}
	drop s1_* s0_*
}
* The peer_adj_ret column of each file reproduces the published Tables V-VII.
**** End Tables V-VII with the updated benchmark ****
