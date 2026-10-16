**** Cross-sectional tests, interaction specification (all Table III controls + fye1 fixed effects) ****
* For each cross-sectional characteristic X, re-estimates the Table III regression with all
* controls and fiscal-year-end date fixed effects, adding X and Conflicted CIO x X. Controls have
* common coefficients for both groups. Regenerates xsec_interactions_fye1.xlsx.
*   Binary X (columns 1-6): newjob = effect of conflict when X = 0, newjob_x = between-group
*     difference, lincom = effect when X = 1.
*   Continuous X (columns 7-8: log CIO total compensation, CIO age): X is centered at its mean in
*     the regression sample, so newjob = effect of conflict at average X and newjob_x = change in
*     that effect per unit of X; lincom gives the effect at the 25th and 75th percentiles of X.
*
* Run AFTER updated_benchmark_tables.do, which creates bench_adj_upd. The panel must be xtset
* (ppd_id fy), as in the main do-file, for the lagged-compensation robustness check.

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* --- cross-sectional characteristics: missing age / funding coded missing -----------------
capture drop young highrate highfund log_comp l_log_comp fy_mean_lc log_comp_rel
generate young = (cio_age<=46) if !missing(cio_age)
generate highrate = (InvestmentReturnAssumption_GASB>0.08) if !missing(InvestmentReturnAssumption_GASB)
generate highfund = (ActFundedRatio_GASB>=92) if !missing(ActFundedRatio_GASB)
* continuous characteristics
generate log_comp = ln(CIO_TotalComp)
label variable log_comp "Log CIO total compensation"
generate l_log_comp = l.log_comp
label variable l_log_comp "Lagged log CIO total compensation"
bysort fy: egen fy_mean_lc = mean(cond(cio_dum==1 & fy<=2020 & curr1==0, log_comp, .))
generate log_comp_rel = log_comp - fy_mean_lc
label variable log_comp_rel "Log CIO total compensation minus fiscal-year mean"

* --- all Table III controls ------------------------------------------------------------------
local full l_investmentreturn_1yr size l_ActFundedRatio_GASB l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl fincenter1 l_log_cio_age l_log_cio_tenure prior_private_exp Elite_inst l_sib1 wstate_political
* for CIO age as X, the lagged log age control is dropped (age enters once, as X)
local full_noage : list full - l_log_cio_age

* --- helper for a continuous X ----------------------------------------------------------------
* contint y x, controls(...) out(file) mode(replace|append) label(text) [extra(vars)]
* extra(): further variables interacted with Conflicted CIO (centered), e.g. size
capture program drop contint
program define contint
	syntax varlist(min=2 max=2), CONTROLS(varlist) OUT(string) MODE(string) LABEL(string) [EXTRA(varlist)]
	tokenize `varlist'
	local y `1'
	local x `2'
	capture drop newjob newjob_x xvar esamp
	capture drop cx_*
	quietly {
		gen newjob = conf_pen_vendor
		gen xvar = `x'
		gen newjob_x = newjob*xvar
		local cx
		foreach e of local extra {
			gen cx_`e' = newjob*`e'
			local cx `cx' cx_`e'
		}
		* pass 1 finds the estimation sample (reghdfe drops singletons); X is then centered on it
		reghdfe `y' newjob newjob_x xvar `controls' `cx' if cio_dum==1 & fy<=2020 & curr1==0, absorb(fye1) vce(cluster ppd_id fy)
		gen byte esamp = e(sample)
		summarize `x' if esamp, detail
		local m   = r(mean)
		local d25 = r(p25) - r(mean)
		local d75 = r(p75) - r(mean)
		replace xvar = `x' - `m'
		replace newjob_x = newjob*xvar
		foreach e of local extra {
			summarize `e' if esamp
			replace cx_`e' = newjob*(`e' - r(mean))
		}
	}
	label variable newjob   "Conflicted CIO"
	label variable newjob_x "Conflicted CIO x X"
	label variable xvar     "X (centered)"
	reghdfe `y' newjob newjob_x xvar `controls' `cx' if cio_dum==1 & fy<=2020 & curr1==0, absorb(fye1) vce(cluster ppd_id fy)
	foreach q in 25 75 {
		if `d`q''<0 lincom newjob - `=abs(`d`q'')'*newjob_x
		else        lincom newjob + `d`q''*newjob_x
		local e`q' = r(estimate)
		local t`q' = r(estimate)/r(se)
	}
	outreg2 using `out', excel label `mode' $cosmetics keep(newjob newjob_x xvar `cx') addstat(Conflict effect at p25 of X, `e25', t-stat p25, `t25', Conflict effect at p75 of X, `e75', t-stat p75, `t75', Mean of X, `m') addtext(X, `label', Controls, All, FYE FE, Yes) stats(coef tstat)
	drop newjob newjob_x xvar esamp `cx'
end

* =====================================================================================
* Interactions sheet: one output file per dependent variable, one column per characteristic
* =====================================================================================
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
	* columns 7-8: continuous characteristics
	contint `y' log_comp, controls(`full')       out($name1) mode(append) label(log_comp centered)
	contint `y' cio_age,  controls(`full_noage') out($name1) mode(append) label(cio_age centered)
}

* =====================================================================================
* Continuous X robustness sheet
* =====================================================================================
foreach y in peer_adj_ret bench_adj_upd {
	global name1 xsecint_cont_robust_`y'
	contint `y' log_comp,     controls(`full')       out($name1) mode(replace) label(1 log_comp)
	contint `y' l_log_comp,   controls(`full')       out($name1) mode(append)  label(2 lagged log_comp)
	contint `y' log_comp_rel, controls(`full')       out($name1) mode(append)  label(3 log_comp minus FY mean)
	contint `y' log_comp,     controls(`full')       out($name1) mode(append)  label(4 log_comp plus Conf x Size) extra(size)
	contint `y' cio_age,      controls(`full_noage') out($name1) mode(append)  label(5 cio_age)
	contint `y' cio_age,      controls(`full')       out($name1) mode(append)  label(6 cio_age with lagged log age)
}
**** End interaction specification ****
