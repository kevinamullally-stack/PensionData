**** First vs. second half of conflicted CIOs' tenures: returns, fees, fee rates, allocations ****
* Regenerates halves_v3_fye1.xlsx.
*   A. Table III sample: Conflicted x First Half and Conflicted x Second Half vs. all other plan-years
*      (FYE FE; plan + FYE FE); test Second = First.
*   B. Conflicted CIOs who have left: Second Half (FYE FE; CIO + FYE FE; CIO + FYE FE, tenure >= 4).
*   C. CIO-level paired comparison (paired t-test, signed-rank test, share increasing).
* Lagged log CIO tenure and age are omitted from the controls because tenure rises mechanically from
* the first to the second half. Allocation outcomes omit the lagged allocations.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd), in the main do-file's scaled data
* (allocations already multiplied by 100).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* --- tenure at departure and halves ---------------------------------------------------------------
foreach v in last_fy max_ten ydep ten_dep second_half spell_id conf_first conf_second conf_undef {
	capture drop `v'
}
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
egen spell_id = group(cio ppd_id)
generate conf_first  = (conf_pen_vendor==1 & second_half==0) if !missing(conf_pen_vendor)
generate conf_second = (conf_pen_vendor==1 & second_half==1) if !missing(conf_pen_vendor)
generate conf_undef  = (conf_pen_vendor==1 & missing(second_half)) if !missing(conf_pen_vendor)

* --- outcomes -------------------------------------------------------------------------------------
foreach v in fee_ratio_pct exp_ratio_pct alt_fee_share alt_pct pe_pct hf_pct {
	capture drop `v'
}
generate fee_ratio_pct = 100*total_fee_pct
generate exp_ratio_pct = 100*exp_ratio
generate alt_fee_share = 100*(RETotal_Fee + PETotal_Fee + HFTotal_Fee)/(EQTotal_Fee + FITotal_Fee + RETotal_Fee + PETotal_Fee + HFTotal_Fee) ///
	if (EQTotal_Fee + FITotal_Fee + RETotal_Fee + PETotal_Fee + HFTotal_Fee) > 0
generate alt_pct = RETotal_Actl + PETotal_Actl + HFTotal_Actl + AltMiscTotal_Actl + COMDTotal_Actl
generate pe_pct  = PETotal_Actl
generate hf_pct  = HFTotal_Actl
* asset-class fee rates (%) are in the data: eqfee100 fifee100 refee100 pefee100 hffee100

* --- controls ----------------------------------------------------------------------------------------
local c1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
local c2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
local cR `c1' `c2' fincenter1 prior_private_exp Elite_inst l_sib1 wstate_political
local cA `c1' fincenter1 prior_private_exp Elite_inst l_sib1 wstate_political
local outR peer_adj_ret bench_adj_upd fee_ratio_pct exp_ratio_pct eqfee100 fifee100 refee100 pefee100 hffee100 alt_fee_share
local outA alt_pct pe_pct hf_pct
global samp "cio_dum==1 & fy<=2020 & curr1==0"
global csamp "cio_dum==1 & fy<=2020 & curr1==0 & conf_pen_vendor==1 & curr==0 & !missing(second_half)"

* =====================================================================================
* A. Versus all other plan-years
* =====================================================================================
global name1 halves_v3_A
local mode replace
foreach y in `outR' `outA' {
	local ctl `cR'
	if strpos(" `outA' ", " `y' ") local ctl `cA'
	foreach fe in "fye1" "ppd_id fye1" {
		reghdfe `y' conf_first conf_second conf_undef `ctl' if $samp, absorb(`fe') vce(cluster ppd_id fy)
		lincom conf_second - conf_first
		local d  = r(estimate)
		local td = r(estimate)/r(se)
		local pd = r(p)
		outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_first conf_second) ///
			addstat(Second minus first, `d', t, `td', p, `pd') addtext(Outcome, `y', FE, `fe') `mode'
		local mode append
	}
}

* =====================================================================================
* B. Within conflicted CIOs
* =====================================================================================
global name1 halves_v3_B
local mode replace
foreach y in `outR' `outA' {
	local ctl `cR'
	if strpos(" `outA' ", " `y' ") local ctl `cA'
	reghdfe `y' second_half `ctl' if $csamp, absorb(fye1) vce(cluster ppd_id fy)
	outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(second_half) addtext(Outcome, `y', FE, fye1) `mode'
	local mode append
	reghdfe `y' second_half `ctl' if $csamp, absorb(spell_id fye1) vce(cluster ppd_id fy)
	outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(second_half) addtext(Outcome, `y', FE, CIO + fye1) append
	reghdfe `y' second_half `ctl' if $csamp & ten_dep>=4, absorb(spell_id fye1) vce(cluster ppd_id fy)
	outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(second_half) addtext(Outcome, `y', FE, CIO + fye1, Tenure at departure, >=4) append
}

* =====================================================================================
* C. CIO-level paired comparison
* =====================================================================================
foreach y in `outR' `outA' {
	preserve
	keep if $csamp & !missing(`y')
	collapse (mean) `y', by(cio fy second_half)
	collapse (mean) `y', by(cio second_half)
	reshape wide `y', i(cio) j(second_half)
	keep if !missing(`y'0, `y'1)
	display _n as text "==== `y' ===="
	summarize `y'0 `y'1
	ttest `y'1 == `y'0
	signrank `y'1 = `y'0
	count if `y'1 > `y'0
	restore
}
**** End halves ****
