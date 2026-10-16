**** Cross-sectional tests, interaction specification (all Table III controls + fye1 fixed effects) ****
* For each cross-sectional characteristic X, re-estimates the Table III regression with all
* controls and fiscal-year-end date fixed effects, adding X and Conflicted CIO x X. Controls have
* common coefficients for both groups. newjob_x is the between-group difference; lincom gives the
* effect of conflict when X = 1. Regenerates xsec_interactions_fye1.xlsx.
*
* Run AFTER updated_benchmark_tables.do, which creates bench_adj_upd.

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* --- cross-sectional characteristics: missing age / funding coded missing -----------------
capture drop young highrate highfund
generate young = (cio_age<=46) if !missing(cio_age)
generate highrate = (InvestmentReturnAssumption_GASB>0.08) if !missing(InvestmentReturnAssumption_GASB)
generate highfund = (ActFundedRatio_GASB>=92) if !missing(ActFundedRatio_GASB)

* --- all Table III controls ------------------------------------------------------------------
local full l_investmentreturn_1yr size l_ActFundedRatio_GASB l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl fincenter1 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst l_sib1 wstate_political

* One output file per dependent variable; one column per characteristic
foreach y in peer_adj_ret bench_adj_upd {
	global name1 xsecint_fye1_`y'
	local first 1
	foreach s in underpaid young prior_private_exp fincenter1 highrate highfund {
		* X enters once, as its own main effect, so drop it from the controls if it is one
		local fullS : list full - s
		capture drop newjob newjob_x xvar
		gen newjob = conf_pen_vendor
		gen newjob_x = conf_pen_vendor*`s'
		gen xvar = `s'
		label variable newjob   "Conflicted CIO"
		label variable newjob_x "Conflicted CIO x X"
		label variable xvar     "X"
		reghdfe `y' newjob newjob_x xvar `fullS' if cio_dum==1 & fy<=2020 & curr1==0, absorb(fye1) vce(cluster ppd_id fy)
		lincom newjob + newjob_x
		local e1 = r(estimate)
		local t1 = r(estimate)/r(se)
		if `first' outreg2 using $name1, excel label replace $cosmetics keep(newjob newjob_x xvar) addstat(Conflict effect when X=1, `e1', t-stat, `t1') addtext(X, `s', Controls, All, FYE FE, Yes) stats(coef tstat)
		else      outreg2 using $name1, excel label append  $cosmetics keep(newjob newjob_x xvar) addstat(Conflict effect when X=1, `e1', t-stat, `t1') addtext(X, `s', Controls, All, FYE FE, Yes) stats(coef tstat)
		local first 0
		drop newjob newjob_x xvar
	}
}
**** End interaction specification ****
