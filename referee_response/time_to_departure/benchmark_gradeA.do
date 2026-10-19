**** Benchmark confidence: grade A only and reported only ****
* Regenerates benchmark_gradeA_tables.xlsx: correlations with the peer-adjusted return, Table III
* (Panel A peer-adjusted, Panel B benchmark-adjusted), and the interaction specification, for the
* peer-adjusted return (all plan-years; plan-years with bench_adj_updA) and three versions of the
* updated benchmark:
*   bench_adj_upd   reported benchmark, else inferred value graded A or B (earlier tables)
*   bench_adj_updA  reported benchmark, else inferred value graded A
*   bench_adj_rep   reported benchmark only
*
* Run AFTER updated_benchmark_tables.do (merges the benchmark file, creates bench_adj_upd) and
* xsec_interactions.do (defines the contint program and creates young, highrate, highfund,
* log_comp and rel_pay_f). log_cio_age is in the main dataset.

capture confirm variable bench_adj_upd rel_pay_f inferred_estimate_grade
if _rc {
	display as error "run updated_benchmark_tables.do and xsec_interactions.do first"
	exit 111
}
capture program list contint
if _rc {
	display as error "run xsec_interactions.do first (it defines the contint program)"
	exit 111
}

* --- benchmark versions ------------------------------------------------------------------
capture drop bm_updA bench_adj_updA bench_adj_rep
generate bm_updA = total_fund_benchmark_return_pct
replace  bm_updA = inferred_benchmark_return_pct if missing(bm_updA) & inferred_estimate_grade=="A"
generate bench_adj_updA = investmentreturn_1yr - bm_updA
label variable bench_adj_updA "Benchmark-adjusted return, reported or grade A inferred benchmark (%)"
generate bench_adj_rep = investmentreturn_1yr - total_fund_benchmark_return_pct
label variable bench_adj_rep "Benchmark-adjusted return, reported benchmark only (%)"
capture drop peer_cs
generate peer_cs = peer_adj_ret if !missing(bench_adj_updA)
label variable peer_cs "Peer-adjusted return, plan-years with the grade A benchmark-adjusted return"
count if cio_dum==1 & fy<=2020 & curr1==0 & missing(total_fund_benchmark_return_pct) & inferred_estimate_grade=="B" & !missing(inferred_benchmark_return_pct)

* =====================================================================================
* 1. Correlations with the peer-adjusted return (Table III sample, pairwise)
* =====================================================================================
foreach v in bench_adj_upd bench_adj_updA bench_adj_rep {
	display _n as text "---- `v' ----"
	pwcorr peer_adj_ret `v' if cio_dum==1 & fy<=2020 & curr1==0, obs
	spearman peer_adj_ret `v' if cio_dum==1 & fy<=2020 & curr1==0
	pwcorr peer_adj_ret `v' if cio_dum==1 & fy<=2020 & curr1==0 & conf_pen_vendor==1
	pwcorr peer_adj_ret `v' if cio_dum==1 & fy<=2020 & curr1==0 & conf_pen_vendor==0
	* within fiscal-year-end date (fye1) and within fiscal year (fy): demean both returns on the pairwise sample
	foreach g in fye1 fy {
		preserve
		keep if cio_dum==1 & fy<=2020 & curr1==0 & !missing(peer_adj_ret, `v')
		bysort `g': egen m_p = mean(peer_adj_ret)
		bysort `g': egen m_b = mean(`v')
		generate dm_p = peer_adj_ret - m_p
		generate dm_b = `v' - m_b
		display "within `g':"
		correlate dm_p dm_b
		restore
	}
}

* =====================================================================================
* 2. Table III: Panel A (peer_adj_ret, peer_cs) and Panel B (benchmark versions)
* =====================================================================================
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst
global controls5 l_sib1 wstate_political
foreach y in peer_adj_ret peer_cs bench_adj_upd bench_adj_updA bench_adj_rep {
	global name1 table3_gradeA_`y'
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

* =====================================================================================
* 3. Interaction specification (all Table III controls), run with fiscal-year-end date FE
*    (benchmark_gradeA_tables.xlsx) and with fiscal-year FE (benchmark_gradeA_tables_fy.xlsx)
* =====================================================================================
local full l_investmentreturn_1yr size l_ActFundedRatio_GASB l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl fincenter1 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst l_sib1 wstate_political
local full_noage : list full - l_log_cio_age
foreach fe in fye1 fy {
foreach y in peer_adj_ret peer_cs bench_adj_upd bench_adj_updA bench_adj_rep {
	global name1 xsecint_gradeA_`fe'_`y'
	local first 1
	foreach s in underpaid young prior_private_exp fincenter1 highrate highfund {
		local fullS : list full - s
		capture drop newjob newjob_x xvar
		gen newjob = conf_pen_vendor
		gen newjob_x = conf_pen_vendor*`s'
		gen xvar = `s'
		label variable newjob   "Conflicted CIO"
		label variable newjob_x "Conflicted CIO x X"
		label variable xvar     "X"
		reghdfe `y' newjob newjob_x xvar `fullS' if cio_dum==1 & fy<=2020 & curr1==0, absorb(`fe') vce(cluster ppd_id fy)
		lincom newjob + newjob_x
		local e1 = r(estimate)
		local t1 = r(estimate)/r(se)
		if `first' outreg2 using $name1, excel label replace $cosmetics keep(newjob newjob_x xvar) addstat(Conflict effect when X=1, `e1', t-stat, `t1') addtext(X, `s', Controls, All, FE, `fe') stats(coef tstat)
		else      outreg2 using $name1, excel label append  $cosmetics keep(newjob newjob_x xvar) addstat(Conflict effect when X=1, `e1', t-stat, `t1') addtext(X, `s', Controls, All, FE, `fe') stats(coef tstat)
		local first 0
		drop newjob newjob_x xvar
	}
	contint `y' log_comp,  controls(`full')       out($name1) mode(append) label(log_comp centered) absorb(`fe')
	contint `y' rel_pay_f, controls(`full')       out($name1) mode(append) label(rel_pay_f centered) absorb(`fe')
	* log CIO age: the paper's log_cio_age, ln(1 + age); the lagged log age control is dropped
	contint `y' log_cio_age, controls(`full_noage') out($name1) mode(append) label(log_cio_age centered) absorb(`fe')
}
}
**** End benchmark confidence ****
