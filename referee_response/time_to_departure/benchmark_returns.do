**** Tables B1-B5: Benchmark returns of conflicted vs unconflicted CIOs, and across cross-sectional groups ****
* Append to ConflictedCIOs_8Oct2025.do after the Table 3 block: uses the same scaling, lags, controls
* globals, sample filter (cio_dum==1 & fy<=2020 & curr1==0) and clustering (ppd_id fy).
* Dependent variable: the plan's total-fund POLICY BENCHMARK return in percent (fund_benchmark*100).
* Every regression absorbs fiscal-year-END-DATE effects (fye1), so plans are compared only with plans
* whose fiscal year covers the same twelve months (the same convention as the peer adjustment).

* --- variables -----------------------------------------------------------------
generate bench_ret_pct = 100*fund_benchmark
label variable bench_ret_pct "Policy benchmark return (%)"
egen fye_id = group(fye1)
* target (policy) allocations in percent; cash omitted from regressions because weights sum to 100
foreach v in EQTotal FITotal RETotal PETotal HFTotal AltMiscTotal COMDTotal CashTotal {
	generate t_`v' = 100*`v'_Trgt
}
global tgt t_EQTotal t_FITotal t_RETotal t_PETotal t_HFTotal t_AltMiscTotal t_COMDTotal
* split indicators as in Tables V-VII (young uses the do-file's cutoff; highfund uses the scaled funding ratio)
capture drop young highrate highfund
generate young = (cio_age<=46) if !missing(cio_age)
generate highrate = (InvestmentReturnAssumption_GASB>0.08) if !missing(InvestmentReturnAssumption_GASB)
generate highfund = (ActFundedRatio_GASB>=92) if !missing(ActFundedRatio_GASB)

global samp3 "cio_dum==1 & fy<=2020 & curr1==0"
global c3all l_investmentreturn_1yr size l_ActFundedRatio_GASB fincenter1 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst l_sib1 wstate_political

* --- Table B1: conflicted vs unconflicted ------------------------------------------
global name1 tableB1
reghdfe bench_ret_pct conf_pen_vendor if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label replace $cosmetics keep(conf_pen_vendor) addtext(Target alloc., No, Table III ctrls, No, Plan FE, No, FYE FE, Yes) stats(coef tstat)
reghdfe bench_ret_pct conf_pen_vendor $tgt if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep(conf_pen_vendor $tgt) addtext(Target alloc., Yes, Table III ctrls, No, Plan FE, No, FYE FE, Yes) stats(coef tstat)
reghdfe bench_ret_pct conf_pen_vendor $tgt $c3all if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep(conf_pen_vendor $tgt $c3all) addtext(Target alloc., Yes, Table III ctrls, Yes, Plan FE, No, FYE FE, Yes) stats(coef tstat)
reghdfe bench_ret_pct conf_pen_vendor $tgt $c3all if $samp3, absorb(ppd_id fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep(conf_pen_vendor $tgt $c3all) addtext(Target alloc., Yes, Table III ctrls, Yes, Plan FE, Yes, FYE FE, Yes) stats(coef tstat)
* descriptive: benchmark return minus the leave-one-out mean of plans with the same fiscal-year end
bysort fye_id: egen _s = total(bench_ret_pct)
bysort fye_id: egen _n = count(bench_ret_pct)
generate bench_peeradj = bench_ret_pct - (_s - bench_ret_pct)/(_n - 1)
ttest bench_peeradj if $samp3, by(conf_pen_vendor)
drop _s _n

* --- Table B2: cross-sectional groups, paper format (controls interacted with the split) -----
* Control lists follow the corresponding table blocks of the main do-file (controls2 replaced by
* target allocations in Panel B).
local ctrl_underpaid  l_investmentreturn_1yr size l_ActFundedRatio_GASB fincenter1 l_log_cio_tenure l_log_cio_age l_sib1 wstate_political
local ctrl_young      l_investmentreturn_1yr size l_ActFundedRatio_GASB fincenter1 l_sib1 wstate_political
local ctrl_highfund   l_investmentreturn_1yr size fincenter1 l_log_cio_tenure
local ctrl_fincenter1 l_investmentreturn_1yr size l_ActFundedRatio_GASB l_log_cio_tenure l_sib1 wstate_political
local ctrl_prior_private_exp l_investmentreturn_1yr size l_ActFundedRatio_GASB fincenter1 l_log_cio_tenure l_sib1 wstate_political
local ctrl_highrate   l_investmentreturn_1yr size l_ActFundedRatio_GASB fincenter1 l_log_cio_tenure l_sib1 wstate_political
global alloc_lag l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
foreach panel in A B {
	global name1 tableB2`panel'
	local first = 1
	foreach s in underpaid young highfund fincenter1 prior_private_exp highrate {
		if "`panel'"=="A" local cl `ctrl_`s'' $alloc_lag
		if "`panel'"=="B" local cl `ctrl_`s'' $tgt
		capture drop g1_* g0_*
		foreach var in conf_pen_vendor `cl' {
			gen g1_`var' = `s'*`var'
			gen g0_`var' = (1-`s')*`var'
		}
		reghdfe bench_ret_pct g1_conf_pen_vendor g0_conf_pen_vendor `s' g1_* g0_* if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
		test g1_conf_pen_vendor = g0_conf_pen_vendor
		local p1 = r(p)
		if `first' outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(g1_conf_pen_vendor g0_conf_pen_vendor) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Split, `s') replace
		else      outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(g1_conf_pen_vendor g0_conf_pen_vendor) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Split, `s') append
		local first = 0
	}
	capture drop g1_* g0_*
}

* --- Table B3: among conflicted CIOs only --------------------------------------------
global name1 tableB3
local first = 1
foreach s in underpaid young highfund fincenter1 prior_private_exp highrate {
	local c3 : list global(c3all) - s
	reghdfe bench_ret_pct `s' if $samp3 & conf_pen_vendor==1, absorb(fye_id) vce(cluster ppd_id fy)
	if `first' outreg2 using $name1, excel label replace $cosmetics keep(`s') addtext(Controls, None) stats(coef tstat)
	else      outreg2 using $name1, excel label append  $cosmetics keep(`s') addtext(Controls, None) stats(coef tstat)
	local first = 0
	reghdfe bench_ret_pct `s' $tgt if $samp3 & conf_pen_vendor==1, absorb(fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep(`s') addtext(Controls, Target alloc.) stats(coef tstat)
	reghdfe bench_ret_pct `s' $tgt `c3' if $samp3 & conf_pen_vendor==1, absorb(fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep(`s') addtext(Controls, Target alloc. + Table III) stats(coef tstat)
}

* --- Tables B4-B5: asset-class benchmark (index) returns from benchmarks_collected.csv ----------
preserve
import delimited "benchmarks_collected.csv", clear varnames(1) case(preserve)
keep ppd_id fy us_equity_benchmark_return_pct intl_equity_benchmark_return_pct fixed_income_benchmark_return_pct real_estate_benchmark_return_pct private_equity_benchmark_return_pct hedge_fund_absolute_return_benchmark_return_pct total_fund_benchmark_return_pct
rename (us_equity_benchmark_return_pct intl_equity_benchmark_return_pct fixed_income_benchmark_return_pct real_estate_benchmark_return_pct private_equity_benchmark_return_pct hedge_fund_absolute_return_benchmark_return_pct total_fund_benchmark_return_pct) (bx_us bx_intl bx_fi bx_re bx_pe bx_hf bx_tot)
tempfile bx
save `bx'
restore
merge 1:1 ppd_id fy using `bx', keep(master match) nogenerate
label variable bx_us "U.S. equity benchmark return (%)"
label variable bx_intl "International equity benchmark return (%)"
label variable bx_fi "Fixed income benchmark return (%)"
label variable bx_re "Real estate benchmark return (%)"
label variable bx_pe "Private equity benchmark return (%)"
label variable bx_hf "Hedge fund benchmark return (%)"
label variable bx_tot "Total fund benchmark return, collected file (%)"

global name1 tableB4
local first = 1
foreach v in bx_us bx_intl bx_fi bx_re bx_pe bx_hf bx_tot {
	reghdfe `v' conf_pen_vendor if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
	if `first' outreg2 using $name1, excel label replace $cosmetics keep(conf_pen_vendor) addtext(Dep. var., `v', Controls, None) stats(coef tstat)
	else      outreg2 using $name1, excel label append  $cosmetics keep(conf_pen_vendor) addtext(Dep. var., `v', Controls, None) stats(coef tstat)
	local first = 0
	reghdfe `v' conf_pen_vendor $tgt $c3all if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep(conf_pen_vendor) addtext(Dep. var., `v', Controls, Target alloc. + Table III) stats(coef tstat)
}

global name1 tableB5
local first = 1
foreach s in underpaid young highfund fincenter1 prior_private_exp {
	local cl `ctrl_`s'' $tgt
	capture drop g1_* g0_*
	foreach var in conf_pen_vendor `cl' {
		gen g1_`var' = `s'*`var'
		gen g0_`var' = (1-`s')*`var'
	}
	foreach v in bx_us bx_intl bx_fi bx_re bx_pe bx_hf {
		capture noisily reghdfe `v' g1_conf_pen_vendor g0_conf_pen_vendor `s' g1_* g0_* if $samp3, absorb(fye_id) vce(cluster ppd_id fy)
		if _rc==0 {
			capture test g1_conf_pen_vendor = g0_conf_pen_vendor
			local p1 = r(p)
			if `first' outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(g1_conf_pen_vendor g0_conf_pen_vendor) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Split, `s', Dep. var., `v') replace
			else      outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(g1_conf_pen_vendor g0_conf_pen_vendor) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Split, `s', Dep. var., `v') append
			local first = 0
		}
	}
}
capture drop g1_* g0_*
**** End Tables B1-B5 ****
