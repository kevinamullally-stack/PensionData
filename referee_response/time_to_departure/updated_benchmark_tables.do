**** Table III and Tables V-VII with the updated policy benchmark ****
* Regenerates table3_updated_benchmark_v2.xlsx and xsec_updated_benchmark_tables_v2.xlsx.
* Supersedes table3_updated_benchmark.do and xsec_updated_benchmark.do.
*
* Append to ConflictedCIOs_8Oct2025.do AFTER the Table 3 block: it relies on that file's scaling
* (investmentreturn_1yr and ActFundedRatio_GASB already multiplied by 100), lags, globals and
* sample filter. Put benchmarks_with_inferred.csv (version of Oct 16) in the working directory.
*
* Updated benchmark = benchmark return reported in the plan's financial report; where none is
* stated, the inferred value if it is graded A or B. Grade C inferred values are not used.

* --- guard: returns must already be in percent ----------------------------------------
quietly summarize investmentreturn_1yr
if r(mean) < 1 {
	display as error "investmentreturn_1yr is not in percent; run this block after the scaling loop"
	exit 459
}

* =====================================================================================
* 1. Updated benchmark and benchmark-adjusted returns
* =====================================================================================
preserve
import delimited "benchmarks_with_inferred.csv", clear varnames(1) case(preserve) bindquote(strict) maxquotedrows(unlimited)
keep ppd_id fy total_fund_benchmark_return_pct inferred_benchmark_return_pct inferred_estimate_grade total_fund_actual_return_pct
destring total_fund_benchmark_return_pct inferred_benchmark_return_pct total_fund_actual_return_pct, replace force
tempfile newbm
save `newbm'
restore
capture drop total_fund_benchmark_return_pct inferred_benchmark_return_pct inferred_estimate_grade total_fund_actual_return_pct
merge 1:1 ppd_id fy using `newbm', keep(master match) nogenerate

capture drop bm_upd bench_adj_upd bench_adj_upd_doc ret_gap
generate bm_upd = total_fund_benchmark_return_pct
replace  bm_upd = inferred_benchmark_return_pct if missing(bm_upd) & inlist(inferred_estimate_grade, "A", "B")
label variable bm_upd "Updated policy benchmark return (%)"
* PPD investment return minus the updated benchmark (Panel B)
generate bench_adj_upd = investmentreturn_1yr - bm_upd
label variable bench_adj_upd "Benchmark-adjusted return, updated benchmark (%)"
* Robustness: the report's own total-fund return minus its benchmark (same page, same fiscal year)
generate bench_adj_upd_doc = total_fund_actual_return_pct - bm_upd
label variable bench_adj_upd_doc "Benchmark-adjusted return, document-matched (%)"

* Coverage and fiscal-year alignment diagnostics
count if cio_dum==1 & fy<=2020 & curr1==0 & !missing(bench_adj_ret_pct)
count if cio_dum==1 & fy<=2020 & curr1==0 & !missing(bench_adj_upd)
generate ret_gap = abs(investmentreturn_1yr - total_fund_actual_return_pct)
count if cio_dum==1 & fy<=2020 & curr1==0 & !missing(bench_adj_upd) & ret_gap>0.5 & !missing(ret_gap)

* =====================================================================================
* 2. Table III: Panel A (peer-adjusted) and Panel B (original, updated, document-matched)
* =====================================================================================
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst
global controls5 l_sib1 wstate_political

foreach y in peer_adj_ret bench_adj_ret_pct bench_adj_upd bench_adj_upd_doc {
	global name1 table3_`y'
	capture drop newjob
	gen newjob = conf_pen_vendor
	reghdfe `y' newjob $controls1 $controls2 $controls3 if cio_dum==1 & fy<=2020 & curr1==0, absorb(fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label replace $cosmetics keep(newjob $controls2 $controls1 $controls3) addtext(Clustered, Plan & Year, FE, Year) stats(coef tstat)
	reghdfe `y' newjob $controls1 $controls2 $controls3 $controls4 $controls5 if cio_dum==1 & fy<=2020 & curr1==0, absorb(fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(newjob $controls2 $controls1 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, FE, Year) stats(coef tstat)
	reghdfe `y' newjob $controls1 $controls2 $controls3 $controls4 $controls5 if cio_dum==1 & fy<=2020 & curr1==0, absorb(ppd_id) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(newjob $controls2 $controls1 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, FE, Plan) stats(coef tstat)
	reghdfe `y' newjob $controls1 $controls2 $controls3 $controls4 $controls5 if cio_dum==1 & fy<=2020 & curr1==0, absorb(ppd_id fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(newjob $controls2 $controls1 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, FE, Plan & Year) stats(coef tstat)
	drop newjob
	foreach q in 5 10 {
		gen newjob = conf_cio
		replace newjob = 0 if !missing(year_departs) & (conf_cio==1) & (fy<=year_departs-`q')
		reghdfe `y' newjob $controls2 $controls1 $controls3 $controls4 $controls5 if cio_dum==1 & curr1==0 & fy<=2020, absorb(fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(newjob $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, FE, Year, last n years, `q') stats(coef tstat)
		drop newjob
	}
}
* table3_peer_adj_ret and table3_bench_adj_ret_pct reproduce the published Panels A and B.

* =====================================================================================
* 3. Tables V-VII: cross-sectional splits
* =====================================================================================
* Split indicators. Missing CIO age and missing funding ratio are coded missing (not 0/1), and the
* funding indicator is defined from the funding ratio alone.
capture drop young highrate highfund
generate young = (cio_age<=46) if !missing(cio_age)
generate highrate = (InvestmentReturnAssumption_GASB>0.08) if !missing(InvestmentReturnAssumption_GASB)
generate highfund = (ActFundedRatio_GASB>=92) if !missing(ActFundedRatio_GASB)

* Control lists: the globals in effect in each cross-sectional block of the main do-file
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
	foreach y in peer_adj_ret bench_adj_ret_pct bench_adj_upd bench_adj_upd_doc {
		reghdfe `y' s1_conf s0_conf `s' `ints' if cio_dum==1 & curr1==0 & fy<=2020, absorb(fy) vce(cluster `cl')
		test s1_conf = s0_conf
		local p1 = r(p)
		if `first' outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(s1_conf s0_conf) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Dep. var., `y') replace
		else      outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(s1_conf s0_conf) addstat(Adj. R-squared, e(r2_a), p-value equal, `p1') addtext(Dep. var., `y') append
		local first 0
	}
	drop s1_* s0_*
}
**** End ****
