**** Table VIII (exogenous shock) with the updated benchmark and with fiscal-year-end FE ****
* Same specification as the Table 5 / Table VIII block of ConflictedCIOs_8Oct2025.do, run for
* peer_adj_ret (Panel A) and bench_adj_upd (Panel B; PPD return minus the updated benchmark:
* reported, else inferred grade A/B). Columns (1)-(3): year FE, plan FE, plan + year FE (published);
* columns (4)-(5): fiscal-year-end date FE, plan + fiscal-year-end date FE.
* Regenerates tableVIII_updated_benchmark.xlsx. The last block re-reports the tests with standard
* errors clustered by plan only.
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
global controls4 l_log_cio_age l_log_cio_tenure
global controls5 l_sib1 wstate_political

capture drop conf_cio_shock2
generate conf_cio_shock2 = conf_pen_vendor*shock2
label variable conf_cio_shock2 "Conflicted x Shock Period (0/1)"

foreach y in peer_adj_ret bench_adj_upd {
	global name1 exo_shock_upd_`y'
	local mode replace
	foreach fe in "fy" "ppd_id" "ppd_id fy" "fye1" "ppd_id fye1" {
		reghdfe `y' conf_pen_vendor conf_cio_shock2 shock2 $controls1 $controls2 $controls3 $controls4 $controls5 ///
			if cio_dum==1 & curr1==0 & fy<=2020, absorb(`fe') vce(cluster ppd_id fy)
		lincom conf_pen_vendor + conf_cio_shock2
		local s1 = r(estimate)
		test conf_pen_vendor + conf_cio_shock2 = 0
		local p1 = r(p)
		outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) ///
			addstat(Adj. R-squared, e(r2_a), Conflicted + Interaction, `s1', Test1 F, `p1') addtext(FE, `fe') `mode'
		local mode append
	}
}

* robustness: standard errors clustered by plan only
foreach y in peer_adj_ret bench_adj_upd {
	foreach fe in "fy" "ppd_id" "ppd_id fy" "fye1" "ppd_id fye1" {
		quietly reghdfe `y' conf_pen_vendor conf_cio_shock2 shock2 $controls1 $controls2 $controls3 $controls4 $controls5 ///
			if cio_dum==1 & curr1==0 & fy<=2020, absorb(`fe') vce(cluster ppd_id)
		quietly test conf_pen_vendor + conf_cio_shock2 = 0
		display "`y' | FE `fe' | plan-clustered: t(Conflicted) = " %5.2f _b[conf_pen_vendor]/_se[conf_pen_vendor] ///
			", t(Conflicted x Shock) = " %5.2f _b[conf_cio_shock2]/_se[conf_cio_shock2] ", p(sum = 0) = " %5.3f r(p)
	}
}
**** End Table VIII ****
