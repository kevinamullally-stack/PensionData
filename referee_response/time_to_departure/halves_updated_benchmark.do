**** First vs second half of tenure, with the updated benchmark ****
* Regenerates halves_updated_benchmark.xlsx: Table XI-split, XII-split, XI, XII, XIII.
* Same specifications as halves_tables.do; Panel B and Table XIII now use bench_adj_upd
* (PPD return minus the updated benchmark: reported, else inferred grade A/B).
*
* Run AFTER updated_benchmark_tables.do, which creates bench_adj_upd.

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* --- Tenure at departure and the second-half indicator ---------------------------
capture drop last_fy max_ten ydep ten_dep second_half spell_id fee_ratio_pct conf_first conf_second conf_undef
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
label variable second_half "Second Half of Tenure (0/1)"
egen spell_id = group(cio ppd_id)
generate fee_ratio_pct = 100*total_fee_pct

global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst
global controls5 l_sib1 wstate_political

* =====================================================================================
* Table XI-split / XII-split: Table III regressions with Conflicted split by half of tenure
* (omitted category = all non-conflicted plan-years)
* =====================================================================================
generate conf_first  = (conf_pen_vendor==1 & second_half==0) if !missing(conf_pen_vendor)
generate conf_second = (conf_pen_vendor==1 & second_half==1) if !missing(conf_pen_vendor)
generate conf_undef  = (conf_pen_vendor==1 & missing(second_half)) if !missing(conf_pen_vendor)
label variable conf_first  "Conflicted CIO x First Half of Tenure (0/1)"
label variable conf_second "Conflicted CIO x Second Half of Tenure (0/1)"
global x conf_first conf_second conf_undef
global samp3 "cio_dum==1 & fy<=2020 & curr1==0"
foreach y in peer_adj_ret bench_adj_upd fee_ratio_pct {
	global name1 tableXIsplit_`y'
	reghdfe `y' $x $controls1 $controls2 $controls3 if $samp3, absorb(fy) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label replace $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3) addtext(Plan FE, No, Year FE, Yes) addstat(p-value First=Second, `p1') stats(coef tstat)
	reghdfe `y' $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp3, absorb(fy) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label append $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Plan FE, No, Year FE, Yes) addstat(p-value First=Second, `p1') stats(coef tstat)
	reghdfe `y' $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp3, absorb(ppd_id) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label append $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Plan FE, Yes, Year FE, No) addstat(p-value First=Second, `p1') stats(coef tstat)
	reghdfe `y' $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp3, absorb(ppd_id fy) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label append $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Plan FE, Yes, Year FE, Yes) addstat(p-value First=Second, `p1') stats(coef tstat)
}

* =====================================================================================
* Table XI / XII: conflicted CIOs only, second half vs first half
* =====================================================================================
global samp "cio_dum==1 & fy<=2020 & curr1==0 & conf_pen_vendor==1 & curr==0 & !missing(second_half)"
foreach y in peer_adj_ret bench_adj_upd fee_ratio_pct {
	global name1 tableXI_`y'
	reghdfe `y' second_half $controls1 $controls2 $controls3 if $samp, absorb(fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label replace $cosmetics keep(second_half $controls1 $controls2 $controls3) addtext(Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
	reghdfe `y' second_half $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(second_half $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
	reghdfe `y' second_half $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(second_half $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Plan FE, Yes, Year FE, No, CIO FE, No) stats(coef tstat)
	reghdfe `y' second_half $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(second_half $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Plan FE, Yes, Year FE, Yes, CIO FE, No) stats(coef tstat)
	reghdfe `y' second_half $controls1 $controls2 $controls3 if $samp, absorb(spell_id fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(second_half $controls1 $controls2 $controls3) addtext(Plan FE, No, Year FE, Yes, CIO FE, Yes) stats(coef tstat)
	reghdfe `y' second_half $controls1 $controls2 $controls3 if $samp & ten_dep>=4, absorb(spell_id fy) vce(cluster ppd_id fy)
		outreg2 using $name1, excel label append $cosmetics keep(second_half $controls1 $controls2 $controls3) addtext(Plan FE, No, Year FE, Yes, CIO FE, Yes, Min. tenure at departure, 4) stats(coef tstat)
}

* =====================================================================================
* Table XIII: one observation per conflicted CIO, first vs second half
* =====================================================================================
preserve
keep if $samp
collapse (mean) peer_adj_ret bench_adj_upd fee_ratio_pct, by(cio fy second_half)
collapse (mean) peer_adj_ret bench_adj_upd fee_ratio_pct, by(cio second_half)
reshape wide peer_adj_ret bench_adj_upd fee_ratio_pct, i(cio) j(second_half)
foreach v in peer_adj_ret bench_adj_upd fee_ratio_pct {
	generate d_`v' = `v'1 - `v'0
	ttest `v'1 == `v'0 if !missing(`v'0, `v'1)
	signrank `v'1 = `v'0 if !missing(`v'0, `v'1)
	count if d_`v'>0 & !missing(d_`v')
}
restore
**** End halves with the updated benchmark ****
