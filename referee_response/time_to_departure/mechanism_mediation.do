**** Mechanism: does the conflicted underperformance run through fees/allocations, and does it accelerate? ****
* Regenerates mechanism_mediation.xlsx for peer_adj_ret and bench_adj_upd.
*   A. Mediation: Table III regression (fye1 FE; plan + fye1 FE) on a common sample with non-missing
*      Fee Ratio, Fee Slope and alternatives share; Conflicted CIO without allocation controls, with
*      Table III controls, and adding Fee Ratio, Fee Slope (slope_fee_pct_controls), alternatives share,
*      and all three. Change in the Conflicted coefficient vs. Table III controls: plan-block bootstrap.
*      Path a: each mediator regressed on Conflicted CIO with the same controls (alternatives share
*      without allocation controls).
*   B. Timing: Conflicted CIO level effect and x First Half / x Second Half for returns, Fee Ratio and
*      alternatives share; equal-weighted within-CIO halves change (CIO + fye1 FE) for departed CIOs.
* SE double clustered by plan and year.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd), in the main do-file's scaled data
* (allocations already multiplied by 100).

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
global full    $controls1 $controls2 $controls3 $controls4 $controls5
global noalloc $controls1 $controls3 $controls4 $controls5
global t3 "cio_dum==1 & fy<=2020 & curr1==0"

* --- variables -------------------------------------------------------------------------------------
foreach v in fee_ratio_pct alt_pct fee_slope last_fy max_ten ydep ten_dep second_half spell_id conf_first conf_second conf_undef conf_sp conf_x_second {
	capture drop `v'
}
generate fee_ratio_pct = 100*total_fee_pct
generate alt_pct = RETotal_Actl + PETotal_Actl + HFTotal_Actl + AltMiscTotal_Actl + COMDTotal_Actl
generate fee_slope = slope_fee_pct_controls
label variable fee_ratio_pct "Fee Ratio (%)"
label variable alt_pct "Alternatives share (%)"
label variable fee_slope "Fee Slope"
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
egen spell_id = group(cio ppd_id)
generate conf_first  = (conf_pen_vendor==1 & second_half==0)
generate conf_second = (conf_pen_vendor==1 & second_half==1)
generate conf_undef  = (conf_pen_vendor==1 & missing(second_half))
bysort spell_id: egen conf_sp = max(conf_pen_vendor)
generate conf_x_second = conf_sp*second_half

* =====================================================================================
* A. Mediation
* =====================================================================================
capture program drop medchange
program define medchange, rclass
	* change in the Conflicted coefficient from Table III controls to Table III controls + mediators
	syntax varname, MED(string) FE(string)
	quietly reghdfe `varlist' conf_pen_vendor $full if msamp, absorb(`fe')
	local b0 = _b[conf_pen_vendor]
	quietly reghdfe `varlist' conf_pen_vendor $full `med' if msamp, absorb(`fe')
	return scalar diff = `b0' - _b[conf_pen_vendor]
end

foreach y in peer_adj_ret bench_adj_upd {
	foreach fe in "fye1" "ppd_id fye1" {
		capture drop msamp
		* common sample: every column uses the same plan-years
		quietly reghdfe `y' conf_pen_vendor $full fee_ratio_pct fee_slope alt_pct if $t3, absorb(`fe')
		generate msamp = e(sample)
		local nm med_`y'_`=subinstr("`fe'"," ","_",.)'
		reghdfe `y' conf_pen_vendor $noalloc if msamp, absorb(`fe') vce(cluster ppd_id fy)
		outreg2 using `nm', excel replace stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) bdec(3) keep(conf_pen_vendor) addtext(Controls, No allocations, FE, `fe')
		reghdfe `y' conf_pen_vendor $full if msamp, absorb(`fe') vce(cluster ppd_id fy)
		outreg2 using `nm', excel append stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) bdec(3) keep(conf_pen_vendor) addtext(Controls, Table III, FE, `fe')
		foreach med in "fee_ratio_pct" "fee_slope" "alt_pct" "fee_ratio_pct fee_slope alt_pct" {
			reghdfe `y' conf_pen_vendor $full `med' if msamp, absorb(`fe') vce(cluster ppd_id fy)
			outreg2 using `nm', excel append stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) bdec(3) keep(conf_pen_vendor `med') addtext(Controls, Table III + mediators, FE, `fe')
			* plan-block bootstrap of the change in the Conflicted coefficient (clusters resampled with new plan ids)
			preserve
			keep if msamp
			generate pid_b = ppd_id
			local feb = subinstr("`fe'","ppd_id","pid_b",.)
			bootstrap diff=r(diff), reps(500) seed(20261026) cluster(ppd_id) idcluster(pid_b): medchange `y', med(`med') fe(`feb')
			restore
		}
		* path a: does Conflicted predict each mediator?
		reghdfe fee_ratio_pct conf_pen_vendor $full if msamp, absorb(`fe') vce(cluster ppd_id fy)
		reghdfe fee_slope conf_pen_vendor $full if msamp, absorb(`fe') vce(cluster ppd_id fy)
		reghdfe alt_pct conf_pen_vendor $noalloc if msamp, absorb(`fe') vce(cluster ppd_id fy)
	}
}

* =====================================================================================
* B. Timing: level effect, halves, and equal-weighted within-CIO halves change
* =====================================================================================
foreach y in peer_adj_ret bench_adj_upd fee_ratio_pct alt_pct {
	local ctl $full
	if "`y'"=="alt_pct" local ctl $noalloc
	foreach fe in "fye1" "ppd_id fye1" {
		reghdfe `y' conf_pen_vendor `ctl' if $t3, absorb(`fe') vce(cluster ppd_id fy)
		reghdfe `y' conf_first conf_second conf_undef `ctl' if $t3, absorb(`fe') vce(cluster ppd_id fy)
		lincom conf_second - conf_first
	}
	* equal-weighted within-CIO halves change, departed CIOs, CIO + fye1 FE (each spell-half weighted equally)
	preserve
	keep if $t3 & curr==0 & !missing(second_half) & !missing(`y')
	forvalues i = 1/5 {
		bysort spell_id: drop if _N==1
		bysort fye1: drop if _N==1
	}
	bysort spell_id second_half: generate w_half = 1/_N
	reghdfe `y' second_half conf_x_second [aw=w_half], absorb(spell_id fye1) vce(cluster ppd_id fy)
	lincom second_half + conf_x_second
	restore
}
* Fee Slope at the CIO-plan level: conflicted vs. other CIO-plans
preserve
keep if $t3 & !missing(fee_slope)
bysort spell_id: keep if _n==1
tabstat fee_slope, by(conf_sp) stat(mean median n)
regress fee_slope conf_sp, vce(cluster ppd_id)
ranksum fee_slope, by(conf_sp)
restore
**** End ****
