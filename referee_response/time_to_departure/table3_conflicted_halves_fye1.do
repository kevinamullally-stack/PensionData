**** Table III (columns 2-4) with Conflicted CIO split into halves of tenure: FYE FE and CIO FE ****
* Regenerates table3_conflicted_halves_fye1.xlsx: Panel A peer_adj_ret, Panel B bench_adj_upd.
*   (1) fiscal-year-end date FE; (2) plan FE; (3) plan + fiscal-year-end date FE;
*   (4) conflicted CIOs' plan-years only, CIO (CIO-plan spell) + fiscal-year-end date FE.
* Conflicted CIO is replaced by x First Half and x Second Half of the CIO's tenure at the plan
* (second half = years in which tenure exceeds half of tenure at departure, as in halves_v3_fye1.do).
* Columns 1-3: reference group = non-conflicted plan-years. Column 4: conflicted plan-years only, First
* Half is the reference; Financial Center, Prior Private Experience and Elite College are absorbed by the
* CIO FE and dropped (rows still require them non-missing, as in columns 1-3).
* Versions: Table III controls; without log CIO tenure and age.
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

foreach ver in full noten {
	local tv l_log_cio_age l_log_cio_tenure
	if "`ver'"=="noten" local tv
	local ctl  $controls1 $controls2 $controls3 `tv' prior_private_exp Elite_inst $controls5
	* column 4 drops the controls that do not vary within a CIO's tenure
	local ctlw $controls1 $controls2 `tv' $controls5
	foreach y in peer_adj_ret bench_adj_upd {
		local nm t3_halves_fye1_`ver'_`y'
		local mode replace
		foreach fe in "fye1" "ppd_id" "ppd_id fye1" {
			reghdfe `y' conf_first conf_second conf_undef `ctl' if $t3, absorb(`fe') vce(cluster ppd_id fy)
			lincom conf_second - conf_first
			local d = r(estimate)
			local td = r(estimate)/r(se)
			local p = r(p)
			outreg2 using `nm', excel label `mode' $cosmetics keep(conf_first conf_second `ctl') ///
				addstat(Second minus first, `d', t, `td', p-value, `p', Adj. R-squared, e(r2_a)) addtext(Clustered, Plan & Year, FE, `fe') stats(coef tstat)
			local mode append
		}
		* (4) conflicted CIOs only, CIO + fiscal-year-end date FE: First Half is the reference, so the
		*     coefficient on conf_second (= second_half in this sample) is the within-CIO change
		reghdfe `y' conf_second `ctlw' if $t3 & conf_pen_vendor==1 & !missing(second_half) & !missing(fincenter1, prior_private_exp, Elite_inst), absorb(spell_id fye1) vce(cluster ppd_id fy)
		local d = _b[conf_second]
		local td = _b[conf_second]/_se[conf_second]
		local p = 2*ttail(e(df_r), abs(`td'))
		outreg2 using `nm', excel label append $cosmetics keep(conf_second `ctlw') ///
			addstat(Second minus first, `d', t, `td', p-value, `p', Adj. R-squared, e(r2_a)) addtext(Clustered, Plan & Year, FE, CIO + fye1, Sample, Conflicted CIOs) stats(coef tstat)
	}
}
**** End ****
