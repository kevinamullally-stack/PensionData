**** Returns, first vs. second half of tenure, each CIO weighted equally: CIO and FYE fixed effects ****
* Regenerates returns_halves_equal_weight_fe.xlsx for peer_adj_ret and bench_adj_upd, on all fiscal
* years and excluding fiscal years 2009-2014 (the shock period).
* Sample: CIOs who have left (curr==0) in the Table III sample with defined halves (from full tenure).
* A CIO-plan spell is conflicted if its CIO is a Conflicted CIO (spell maximum of conf_pen_vendor).
*   (a) equal-weighted mean of spell changes (second-half mean minus first-half mean), t-tests, and the
*       same net of the period's fiscal-year-end mean;
*   (b) y = CIO FE + fye1 FE + b*Second Half + d*Conflicted x Second Half, each plan-year weighted by
*       1/(plan-years in its spell-half) so each spell's two halves carry equal weight (with CIO FE alone
*       this equals the equal-weighted mean in (a)); also with lagged plan controls;
*   (c) conflicted CIOs' spells only: y = CIO FE + fye1 FE + b*Second Half (with and without controls).
* CIO FE = CIO-plan spell. SE double clustered by plan and year; plan-only clustering re-reported.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}
foreach v in last_fy max_ten ydep ten_dep second_half spell_id conf_sp conf_x_second {
	capture drop `v'
}
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
egen spell_id = group(cio ppd_id)
bysort spell_id: egen conf_sp = max(conf_pen_vendor)
generate conf_x_second = conf_sp*second_half
global t3 "cio_dum==1 & fy<=2020 & curr1==0"
global pctl l_investmentreturn_1yr size l_ActFundedRatio_GASB l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl l_sib1 wstate_political

capture program drop ewfe
program define ewfe
	* ewfe y [if], [ctl(varlist) conflicted]: equal-weighted CIO FE + fye1 FE halves regression
	syntax varname [if], [CTL(string) CONFLICTED]
	local y `varlist'
	preserve
	keep `if'
	keep if !missing(`y')
	foreach v of local ctl {
		keep if !missing(`v')
	}
	if "`conflicted'"!="" keep if conf_sp==1
	* drop singleton CIO-plan spells and fiscal-year-end groups, then weight each spell-half equally
	forvalues i = 1/5 {
		bysort spell_id: drop if _N==1
		bysort fye1: drop if _N==1
	}
	bysort spell_id second_half: generate w_half = 1/_N
	if "`conflicted'"=="" {
		reghdfe `y' second_half conf_x_second `ctl' [aw=w_half], absorb(spell_id fye1) vce(cluster ppd_id fy)
		lincom second_half + conf_x_second
		quietly reghdfe `y' second_half conf_x_second `ctl' [aw=w_half], absorb(spell_id fye1) vce(cluster ppd_id)
		display "plan-clustered p-value of Conflicted x Second Half = " %5.3f 2*ttail(e(df_r), abs(_b[conf_x_second]/_se[conf_x_second]))
	}
	else {
		reghdfe `y' second_half `ctl' [aw=w_half], absorb(spell_id fye1) vce(cluster ppd_id fy)
		quietly reghdfe `y' second_half `ctl' [aw=w_half], absorb(spell_id fye1) vce(cluster ppd_id)
		display "plan-clustered p-value of Second Half = " %5.3f 2*ttail(e(df_r), abs(_b[second_half]/_se[second_half]))
	}
	restore
end

capture program drop halfdiff_if
program define halfdiff_if
	* equal-weighted mean of spell changes, conflicted vs. other departing CIOs
	syntax varname [if]
	local y `varlist'
	preserve
	keep `if'
	keep if !missing(`y')
	bysort spell_id: generate n = _N
	collapse (mean) v=`y' (first) n ppd_id, by(spell_id conf_sp second_half)
	reshape wide v, i(spell_id conf_sp n ppd_id) j(second_half)
	generate d = v1 - v0
	drop if missing(d)
	display _n as text "==== `y' `if' | equal-weighted spell changes ===="
	ttest d == 0 if conf_sp==1
	ttest d == 0 if conf_sp==0
	ttest d, by(conf_sp)
	ttest d, by(conf_sp) unequal
	ranksum d, by(conf_sp)
	restore
end

foreach per in all ex0914 {
	if "`per'"=="all" global psamp "1"
	else              global psamp "!inrange(fy,2009,2014)"
	global dsamp "$t3 & curr==0 & !missing(second_half) & $psamp"
	foreach y in peer_adj_ret bench_adj_upd {
		display _n as result "################ `y' | `per' ################"
		capture drop m_`y' `y'_dm
		bysort fye1: egen m_`y' = mean(cond($t3 & $psamp, `y', .))
		generate `y'_dm = `y' - m_`y'
		halfdiff_if `y' if $dsamp
		halfdiff_if `y'_dm if $dsamp
		ewfe `y' if $dsamp
		ewfe `y' if $dsamp, ctl($pctl)
		ewfe `y' if $dsamp, conflicted
		ewfe `y' if $dsamp, ctl($pctl) conflicted
	}
}
**** End ****
