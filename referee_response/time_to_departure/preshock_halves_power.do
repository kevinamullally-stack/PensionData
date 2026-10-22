**** Sample composition and power of the first-half vs. second-half tests outside the shock period ****
* Regenerates the counts in preshock_halves_power.xlsx for the full sample, fiscal years through 2008,
* and all years except 2009-2014. Counts use the estimation sample of column 1 (Table III controls,
* fiscal-year-end date FE). Minimum detectable difference (two-sided 5% test, 80% power) =
* (invttail(df, 0.025) + invttail(df, 0.20)) x SE(second minus first), df = year clusters - 1.
*
* Run AFTER table3_conflicted_halves_preshock.do (creates second_half, spell_id, conf_first,
* conf_second, conf_undef, ten_dep).

global ctl l_investmentreturn_1yr size l_ActFundedRatio_GASB l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl fincenter1 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst l_sib1 wstate_political
global t3 "cio_dum==1 & fy<=2020 & curr1==0"

foreach per in full pre2009 ex0914 {
	if "`per'"=="full"         global psamp "1"
	else if "`per'"=="pre2009" global psamp "fy<=2008"
	else                       global psamp "!inrange(fy,2009,2014)"
	foreach y in peer_adj_ret bench_adj_upd {
		foreach v in es c1 c2 s1 s2 tcio tsp tspb tciob {
			capture drop `v'
		}
		quietly reghdfe `y' conf_first conf_second conf_undef $ctl if $t3 & $psamp, absorb(fye1) vce(cluster ppd_id fy)
		generate es = e(sample)
		quietly lincom conf_second - conf_first
		local se  = r(se)
		local df  = r(df)
		local mde = (invttail(`df', 0.025) + invttail(`df', 0.20))*`se'
		display _n as result "################ `per' | `y' ################"
		count if es
		count if es & conf_pen_vendor==1
		count if es & conf_first==1
		count if es & conf_second==1
		* conflicted CIOs, CIO-plan tenures and plans
		egen tcio = tag(cio) if es & conf_pen_vendor==1
		egen tsp  = tag(spell_id) if es & conf_pen_vendor==1
		count if tcio==1
		count if tsp==1
		preserve
		keep if es & conf_pen_vendor==1
		bysort ppd_id: keep if _n==1
		display "plans with a conflicted CIO: " _N
		restore
		* observed in both halves (CIO-plan tenures; CIOs across their plans)
		bysort spell_id: egen s1 = max(es & conf_first)
		bysort spell_id: egen s2 = max(es & conf_second)
		bysort cio: egen c1 = max(es & conf_first)
		bysort cio: egen c2 = max(es & conf_second)
		egen tspb  = tag(spell_id) if s1 & s2
		egen tciob = tag(cio) if c1 & c2
		count if tciob==1
		count if tspb==1
		* tenure
		bysort spell_id: egen npy = total(es & conf_pen_vendor==1)
		summarize npy if tsp==1, detail
		summarize ten_dep if tsp==1, detail
		summarize cio_tenure if es & conf_first==1
		summarize cio_tenure if es & conf_second==1
		drop npy
		display "SE(second minus first) = " %5.3f `se' ", df = `df', minimum detectable difference = " %5.2f `mde'
	}
}
**** End ****
