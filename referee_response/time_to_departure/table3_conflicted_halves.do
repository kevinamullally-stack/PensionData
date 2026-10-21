**** Table III with Conflicted CIO split into the first and second half of tenure ****
* Regenerates table3_conflicted_halves.xlsx: Panel A peer_adj_ret, Panel B bench_adj_upd (updated
* benchmark: reported, else inferred grade A/B). Same columns, controls, sample and clustering as
* Table III; Conflicted CIO (columns 1-4) and its last-5/last-10-year versions (columns 5-6) are each
* replaced by x First Half and x Second Half of the CIO's tenure at the plan.
*   Second half = years in which tenure exceeds half of tenure at departure (as in halves_v3_fye1.do).
*   Conflicted plan-years with undefined halves get their own indicator so the reference group is
*   exactly non-conflicted plan-years (in the current data they all lack lagged controls and drop out).
* Versions: year FE (published), fiscal-year-end date FE, and year FE without log CIO tenure and age.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd and the control globals).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst
global controls5 l_sib1 wstate_political

* --- tenure at departure and halves ---------------------------------------------------------------
foreach v in last_fy max_ten ydep ten_dep second_half {
	capture drop `v'
}
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0

capture program drop t3half
program define t3half
	* t3half y, conf(varname) ctrl(varlist) fe(string) name(string) mode(replace|append) note(string)
	syntax varname, CONF(varname) CTRL(string) FE(string) NAME(string) MODE(string) [NOTE(string)]
	capture drop conf_first conf_second conf_undef
	generate conf_first  = (`conf'==1 & second_half==0)
	generate conf_second = (`conf'==1 & second_half==1)
	generate conf_undef  = (`conf'==1 & missing(second_half))
	label variable conf_first  "Conflicted CIO x First Half of Tenure (0/1)"
	label variable conf_second "Conflicted CIO x Second Half of Tenure (0/1)"
	label variable conf_undef  "Conflicted CIO, halves undefined (0/1)"
	reghdfe `varlist' conf_first conf_second conf_undef `ctrl' if cio_dum==1 & fy<=2020 & curr1==0, absorb(`fe') vce(cluster ppd_id fy)
	lincom conf_second - conf_first
	local d = r(estimate)
	local p = r(p)
	outreg2 using `name', excel label `mode' $cosmetics keep(conf_first conf_second `ctrl') ///
		addstat(Second minus first, `d', p-value, `p', Adj. R-squared, e(r2_a)) addtext(Clustered, Plan & Year, FE, `fe', Conflicted CIO, `note') stats(coef tstat)
end

foreach ver in fy fye1 noten {
	local fe fy
	if "`ver'"=="fye1" local fe fye1
	local c4 $controls4
	if "`ver'"=="noten" local c4 prior_private_exp Elite_inst
	foreach y in peer_adj_ret bench_adj_upd {
		local nm t3_halves_`ver'_`y'
		t3half `y', conf(conf_pen_vendor) ctrl($controls1 $controls2 $controls3) fe(`fe') name(`nm') mode(replace) note(All years)
		t3half `y', conf(conf_pen_vendor) ctrl($controls1 $controls2 $controls3 `c4' $controls5) fe(`fe') name(`nm') mode(append) note(All years)
		t3half `y', conf(conf_pen_vendor) ctrl($controls1 $controls2 $controls3 `c4' $controls5) fe(ppd_id) name(`nm') mode(append) note(All years)
		t3half `y', conf(conf_pen_vendor) ctrl($controls1 $controls2 $controls3 `c4' $controls5) fe(ppd_id `fe') name(`nm') mode(append) note(All years)
		foreach q in 5 10 {
			capture drop newjob
			generate newjob = conf_cio
			replace newjob = 0 if !missing(year_departs) & (conf_cio==1) & (fy<=year_departs-`q')
			t3half `y', conf(newjob) ctrl($controls1 $controls2 $controls3 `c4' $controls5) fe(`fe') name(`nm') mode(append) note(Last `q' years)
			drop newjob
		}
	}
}
**** End ****
