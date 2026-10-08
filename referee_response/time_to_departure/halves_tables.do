**** Tables XI-XIII: Conflicted CIOs, first versus second half of tenure ****
* Append to ConflictedCIOs_8Oct2025.do after the Table 3 block (uses the same
* globals, scaling, lags, sample filter and clustering as Table 3).
* Conflicted CIOs compared with themselves only: the sample is restricted to
* plan-years of conflicted CIOs (conf_pen_vendor==1) who have departed.

* --- Tenure at departure and the second-half indicator ---------------------
* Departure year: year_departs; for non-current CIOs with no recorded departure
* year, fall back to the last fiscal year observed (same convention as the SAS
* time_to_departure code).
bysort cio ppd_id: egen last_fy  = max(fy)
bysort cio ppd_id: egen max_ten  = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
* Tenure at departure = tenure in the last observed year + any gap to the departure year
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
label variable second_half "Second Half of Tenure (0/1)"
egen spell_id = group(cio ppd_id)

* Fee ratio in percent (total_fee_pct is a decimal in Data_v3_3)
generate fee_ratio_pct = 100*total_fee_pct

* Sample: Table 3 sample, conflicted CIOs who have departed
global samp "cio_dum==1 & fy<=2020 & curr1==0 & conf_pen_vendor==1 & curr==0 & !missing(second_half)"

global x second_half
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst
global controls5 l_sib1 wstate_political

* --- Table XI, Panel A: peer-adjusted returns ------------------------------
global y peer_adj_ret
global name1 tableXI_panelA
reghdfe $y $x $controls1 $controls2 $controls3 if $samp, absorb(fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label replace $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, No, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, Yes, CIO FE, No) stats(coef tstat)
* CIO (spell) fixed effects: the profile is identified within each conflicted CIO's own tenure; CIO-level controls omitted
reghdfe $y $x $controls1 $controls2 $controls3 if $samp, absorb(spell_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, Yes) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 if $samp & ten_dep>=4, absorb(spell_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, Yes, Min. tenure at departure, 4) stats(coef tstat)

* --- Table XI, Panel B: benchmark-adjusted returns -------------------------
global y bench_adj_ret_pct
global name1 tableXI_panelB
reghdfe $y $x $controls1 $controls2 $controls3 if $samp, absorb(fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label replace $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, No, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 if $samp, absorb(spell_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, Yes) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 if $samp & ten_dep>=4, absorb(spell_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, Yes, Min. tenure at departure, 4) stats(coef tstat)

* --- Table XII: fee ratio ----------------------------------------------------
global y fee_ratio_pct
global name1 tableXII
reghdfe $y $x $controls1 $controls2 $controls3 if $samp, absorb(fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label replace $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, No, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp, absorb(ppd_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, Yes, CIO FE, No) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 if $samp, absorb(spell_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, Yes) stats(coef tstat)
reghdfe $y $x $controls1 $controls2 $controls3 if $samp & ten_dep>=4, absorb(spell_id fy) vce(cluster ppd_id fy)
	outreg2 using $name1, excel label append $cosmetics keep($x $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes, CIO FE, Yes, Min. tenure at departure, 4) stats(coef tstat)

* --- Table XIII: one observation per CIO, first vs second half ---------------
preserve
keep if $samp
* average across plans within CIO-year (multi-plan systems), then within half
collapse (mean) peer_adj_ret bench_adj_ret_pct fee_ratio_pct, by(cio fy second_half)
collapse (mean) peer_adj_ret bench_adj_ret_pct fee_ratio_pct, by(cio second_half)
reshape wide peer_adj_ret bench_adj_ret_pct fee_ratio_pct, i(cio) j(second_half)
foreach v in peer_adj_ret bench_adj_ret_pct fee_ratio_pct {
	generate d_`v' = `v'1 - `v'0
	ttest `v'1 == `v'0 if !missing(`v'0, `v'1)
	signrank `v'1 = `v'0 if !missing(`v'0, `v'1)
	count if d_`v'>0 & !missing(d_`v')
}
restore
**** End Tables XI-XIII ****

**** Table XI-split / XII-split: Table 3 regressions with Conflicted split into first and second half ****
* Omitted category = all non-conflicted plan-years, exactly as in Table 3.
generate conf_first  = (conf_pen_vendor==1 & second_half==0) if !missing(conf_pen_vendor)
generate conf_second = (conf_pen_vendor==1 & second_half==1) if !missing(conf_pen_vendor)
generate conf_undef  = (conf_pen_vendor==1 & missing(second_half)) if !missing(conf_pen_vendor)   // conflicted, no departure/tenure info (not reported)
label variable conf_first  "Conflicted CIO x First Half of Tenure (0/1)"
label variable conf_second "Conflicted CIO x Second Half of Tenure (0/1)"
global x conf_first conf_second conf_undef
global samp3 "cio_dum==1 & fy<=2020 & curr1==0"
foreach y in peer_adj_ret bench_adj_ret_pct fee_ratio_pct {
	global name1 tableXIsplit_`y'
	reghdfe `y' $x $controls1 $controls2 $controls3 if $samp3, absorb(fy) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label replace $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes) addstat(p-value First=Second, `p1') stats(coef tstat)
	reghdfe `y' $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp3, absorb(fy) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label append $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, No, Year FE, Yes) addstat(p-value First=Second, `p1') stats(coef tstat)
	reghdfe `y' $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp3, absorb(ppd_id) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label append $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, No) addstat(p-value First=Second, `p1') stats(coef tstat)
	reghdfe `y' $x $controls1 $controls2 $controls3 $controls4 $controls5 if $samp3, absorb(ppd_id fy) vce(cluster ppd_id fy)
	test conf_first = conf_second
	local p1 = r(p)
	outreg2 using $name1, excel label append $cosmetics keep(conf_first conf_second $controls1 $controls2 $controls3 $controls4 $controls5) addtext(Clustered, Plan & Year, Plan FE, Yes, Year FE, Yes) addstat(p-value First=Second, `p1') stats(coef tstat)
}
**** End split tables ****
