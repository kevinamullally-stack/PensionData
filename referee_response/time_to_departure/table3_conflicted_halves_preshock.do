**** Table III halves split (FYE FE) on sample periods that avoid the 2009-2014 shock years ****
* Regenerates table3_conflicted_halves_preshock.xlsx. Same specification as
* table3_conflicted_halves_fye1.do, estimated on
*   pre2009 : fiscal years through 2008 (FY2002-2008 with lagged controls)
*   ex0914  : all Table III fiscal years except 2009-2014
* Halves are defined from each CIO's full tenure (all years), so only the estimation sample changes.
*   (1) fiscal-year-end date FE; (2) plan FE; (3) plan + fiscal-year-end date FE;
*   (4) conflicted CIOs' plan-years only, CIO (CIO-plan spell) + fiscal-year-end date FE (First Half
*       is the reference).
* Standard errors double clustered by plan and year (only 7 year clusters before 2009); the last block
* re-reports the second-minus-first tests with standard errors clustered by plan only.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls5 l_sib1 wstate_political

* --- tenure at departure, halves, CIO-plan spell -------------------------------------------------
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
generate conf_first  = (conf_pen_vendor==1 & second_half==0)
generate conf_second = (conf_pen_vendor==1 & second_half==1)
generate conf_undef  = (conf_pen_vendor==1 & missing(second_half))
label variable conf_first  "Conflicted CIO x First Half of Tenure (0/1)"
label variable conf_second "Conflicted CIO x Second Half of Tenure (0/1)"
label variable conf_undef  "Conflicted CIO, halves undefined (0/1)"
global t3 "cio_dum==1 & fy<=2020 & curr1==0"

foreach per in pre2009 ex0914 {
	if "`per'"=="pre2009" global psamp "fy<=2008"
	else                  global psamp "!inrange(fy,2009,2014)"
	foreach ver in full noten {
		local tv l_log_cio_age l_log_cio_tenure
		if "`ver'"=="noten" local tv
		local ctl  $controls1 $controls2 $controls3 `tv' prior_private_exp Elite_inst $controls5
		* column 4 drops the controls that do not vary within a CIO's tenure
		local ctlw $controls1 $controls2 `tv' $controls5
		foreach y in peer_adj_ret bench_adj_upd {
			local nm t3_halves_`per'_`ver'_`y'
			local mode replace
			foreach fe in "fye1" "ppd_id" "ppd_id fye1" {
				reghdfe `y' conf_first conf_second conf_undef `ctl' if $t3 & $psamp, absorb(`fe') vce(cluster ppd_id fy)
				lincom conf_second - conf_first
				local d = r(estimate)
				local td = r(estimate)/r(se)
				local p = r(p)
				outreg2 using `nm', excel label `mode' $cosmetics keep(conf_first conf_second `ctl') ///
					addstat(Second minus first, `d', t, `td', p-value, `p', Adj. R-squared, e(r2_a)) addtext(Clustered, Plan & Year, FE, `fe', Sample, `per') stats(coef tstat)
				local mode append
				quietly reghdfe `y' conf_first conf_second conf_undef `ctl' if $t3 & $psamp, absorb(`fe') vce(cluster ppd_id)
				quietly lincom conf_second - conf_first
				display "`per' `ver' `y' FE `fe': second minus first p-value, clustered by plan = " %5.3f r(p)
			}
			* (4) conflicted CIOs only, CIO + fiscal-year-end date FE: coefficient on conf_second is the within-CIO change
			local c4 $t3 & $psamp & conf_pen_vendor==1 & !missing(second_half) & !missing(fincenter1, prior_private_exp, Elite_inst)
			reghdfe `y' conf_second `ctlw' if `c4', absorb(spell_id fye1) vce(cluster ppd_id fy)
			local d = _b[conf_second]
			local td = _b[conf_second]/_se[conf_second]
			local p = 2*ttail(e(df_r), abs(`td'))
			outreg2 using `nm', excel label append $cosmetics keep(conf_second `ctlw') ///
				addstat(Second minus first, `d', t, `td', p-value, `p', Adj. R-squared, e(r2_a)) addtext(Clustered, Plan & Year, FE, CIO + fye1, Sample, `per' conflicted CIOs) stats(coef tstat)
			quietly reghdfe `y' conf_second `ctlw' if `c4', absorb(spell_id fye1) vce(cluster ppd_id)
			display "`per' `ver' `y' CIO FE: second minus first p-value, clustered by plan = " %5.3f 2*ttail(e(df_r), abs(_b[conf_second]/_se[conf_second]))
		}
	}
}
**** End ****
