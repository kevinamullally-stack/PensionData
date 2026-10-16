**** Table III, Panel B with the updated policy benchmark (benchmarks_with_inferred.csv) ****
* Append to ConflictedCIOs_8Oct2025.do AFTER the Table 3 block. It relies on that file's scaling
* (investmentreturn_1yr already multiplied by 100), lags, globals and sample filter.
* Put benchmarks_with_inferred.csv in the working directory.

* --- guard: the PPD return must already be in percent at this point ------------
quietly summarize investmentreturn_1yr
if r(mean) < 1 {
	display as error "investmentreturn_1yr is not in percent; run this block after the scaling loop"
	exit 459
}

* --- bring in the updated benchmark --------------------------------------------
preserve
import delimited "benchmarks_with_inferred.csv", clear varnames(1) case(preserve) bindquote(strict) maxquotedrows(unlimited)
keep ppd_id fy total_fund_benchmark_return_pct inferred_benchmark_return_pct inferred_estimate_grade total_fund_actual_return_pct
destring total_fund_benchmark_return_pct inferred_benchmark_return_pct total_fund_actual_return_pct, replace force
tempfile newbm
save `newbm'
restore
capture drop total_fund_benchmark_return_pct inferred_benchmark_return_pct inferred_estimate_grade total_fund_actual_return_pct
merge 1:1 ppd_id fy using `newbm', keep(master match) nogenerate

* Updated policy benchmark (percent): reported value; if none, inferred value graded A or B
capture drop bm_upd bench_adj_upd bench_adj_upd_doc
generate bm_upd = total_fund_benchmark_return_pct
replace  bm_upd = inferred_benchmark_return_pct if missing(bm_upd) & inlist(inferred_estimate_grade, "A", "B")
label variable bm_upd "Updated policy benchmark return (%)"

* (1) As requested: PPD investment return minus the updated benchmark
generate bench_adj_upd = investmentreturn_1yr - bm_upd
label variable bench_adj_upd "Benchmark-adjusted return, updated benchmark (%)"
* (2) Document-matched: the report's own total-fund return minus its benchmark (same page, same fiscal year)
generate bench_adj_upd_doc = total_fund_actual_return_pct - bm_upd
label variable bench_adj_upd_doc "Benchmark-adjusted return, document-matched (%)"

* Diagnostics: coverage and fiscal-year alignment between the PPD return and the report's return
count if cio_dum==1 & fy<=2020 & curr1==0 & !missing(bench_adj_ret_pct)
count if cio_dum==1 & fy<=2020 & curr1==0 & !missing(bench_adj_upd)
generate ret_gap = abs(investmentreturn_1yr - total_fund_actual_return_pct)
count if cio_dum==1 & fy<=2020 & curr1==0 & !missing(bench_adj_upd) & ret_gap>0.5 & !missing(ret_gap)
list ppd_id fy investmentreturn_1yr total_fund_actual_return_pct bm_upd bench_adj_ret_pct bench_adj_upd if cio_dum==1 & fy<=2020 & curr1==0 & abs(bench_adj_upd)>10 & !missing(bench_adj_upd), noobs sep(0)

* --- Table III Panel B: original, updated, document-matched --------------------
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst
global controls5 l_sib1 wstate_political

foreach y in bench_adj_ret_pct bench_adj_upd bench_adj_upd_doc {
	global name1 table3b_`y'
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
	* last 5 / 10 years before departure, exactly as in the Table 3 block
	foreach q in 5 10 {
		gen newjob = conf_cio
		replace newjob = 0 if !missing(year_departs) & (conf_cio==1) & (fy<=year_departs-`q')
		reghdfe `y' newjob $controls2 $controls1 $controls3 $controls4 $controls5 if cio_dum==1 & curr1==0 & fy<=2020, absorb(fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(newjob $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, FE, Year, last n years, `q') stats(coef tstat)
		drop newjob
	}
}
* table3b_bench_adj_ret_pct should reproduce the published Panel B exactly.
**** End updated Table III Panel B ****
