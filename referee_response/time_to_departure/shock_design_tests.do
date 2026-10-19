**** Loglisci shock: event study, exposure, and placebo tests (referee Major Concern 2) ****
* Regenerates shock_design_tests.xlsx and the figures shock_eventstudy_fy2008, shock_eventstudy_bins
* and shock_placebo_windows, for peer_adj_ret and bench_adj_upd (PPD return minus the updated
* benchmark: reported, else inferred grade A/B).
*   A. Table VIII, with the full-sample Conflicted coefficient alongside
*   B. Event study, FY2008 base (last fiscal year before the Shock Period), Conflicted main effect
*   C. Event study, two-year bins, FY2007-08 base
*   D. Differential exposure: allocation x Shock Period and allocation x fiscal-year interactions
*   E. Placebo windows: rolling five-year windows; a fake window inside the pre-shock sample
*   F. Placebo groups: other (non-vendor) departures x Shock Period
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd). Requires coefplot (ssc install coefplot).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* controls in effect at Table VIII / Table 5b in the main do-file
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure
global controls5 l_sib1 wstate_political
global ctl $controls1 $controls2 $controls3 $controls4 $controls5
global samp "cio_dum==1 & curr1==0 & fy<=2020"

capture drop confxshock
generate confxshock = conf_pen_vendor*shock2
label variable confxshock "Conflicted CIO x Shock Period"

* =====================================================================================
* A. Table VIII
* =====================================================================================
foreach y in peer_adj_ret bench_adj_upd {
	global name1 shock_tableVIII_`y'
	local mode replace
	foreach fe in "fy" "ppd_id" "ppd_id fy" {
		reghdfe `y' conf_pen_vendor $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
		outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor) addtext(FE, `fe', Shock terms, No) `mode'
		local mode append
		reghdfe `y' conf_pen_vendor confxshock shock2 $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
		lincom conf_pen_vendor + confxshock
		local e1 = r(estimate)
		local t1 = r(estimate)/r(se)
		outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor confxshock) addstat(Effect within Shock Period, `e1', t-stat, `t1') addtext(FE, `fe', Shock terms, Yes) append
	}
}

* =====================================================================================
* B. Event study, FY2008 base, with the Conflicted main effect
* =====================================================================================
capture drop es_*
generate es_pre  = conf_pen_vendor*(fy<2005)
generate es_post = conf_pen_vendor*(fy>2017)
local esvars "es_pre"
local clab ""
forvalues t = 2005/2017 {
	if `t' != 2008 {
		generate es_`t' = conf_pen_vendor*(fy==`t')
		local esvars "`esvars' es_`t'"
		local clab `"`clab' es_`t' = "`t'""'
	}
}
local esvars "`esvars' es_post"
foreach y in peer_adj_ret bench_adj_upd {
	global name1 shock_event_fy2008_`y'
	local mode replace
	foreach fe in "fy" "ppd_id" "ppd_id fy" {
		reghdfe `y' conf_pen_vendor `esvars' $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
		test es_pre es_2005 es_2006 es_2007
		local p_pre = r(p)
		test es_2009 es_2010 es_2011 es_2012 es_2013
		local p_win = r(p)
		test es_2014 es_2015 es_2016 es_2017 es_post
		local p_post = r(p)
		lincom (es_2009 + es_2010 + es_2011 + es_2012 + es_2013)/5
		local wm = r(estimate)
		local wt = r(estimate)/r(se)
		lincom (es_2014 + es_2015 + es_2016 + es_2017)/4
		local pm = r(estimate)
		local pt = r(estimate)/r(se)
		lincom (es_2014 + es_2015 + es_2016 + es_2017)/4 - (es_2009 + es_2010 + es_2011 + es_2012 + es_2013)/5
		local rm = r(estimate)
		local rt = r(estimate)/r(se)
		outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor `esvars') ///
			addstat(Pre-shock leads = 0 p, `p_pre', Shock period = 0 p, `p_win', Post period = 0 p, `p_post', Mean 2009-13, `wm', t, `wt', Mean 2014-17, `pm', t, `pt', Post minus shock mean, `rm', t, `rt') addtext(FE, `fe') `mode'
		local mode append
	}
	* figure from the plan + year FE specification (last estimated); dashed lines bracket FY2009-2013
	local ttl = cond("`y'"=="peer_adj_ret", "A. Peer-adjusted return", "B. Benchmark-adjusted return")
	coefplot, keep(es_20*) vertical yline(0) xline(3.5 8.5, lpattern(dash)) xlabel(, angle(45)) ///
		coeflabels(`clab') xtitle("Fiscal year (FY2008 = 0)") ytitle("Change in the effect of conflict") title("`ttl'", size(medium)) name(es08_`y', replace)
}
graph combine es08_peer_adj_ret es08_bench_adj_upd, ycommon rows(1) title("Event Study Around the Loglisci Shock (FY2008 Base)", size(medium)) xsize(10) ysize(4.2)
graph export "shock_eventstudy_fy2008_stata.png", replace width(2400)

* =====================================================================================
* C. Event study, two-year bins, FY2007-08 base
* =====================================================================================
capture drop bin_*
generate bin_0102 = conf_pen_vendor*inrange(fy,2001,2002)
generate bin_0304 = conf_pen_vendor*inrange(fy,2003,2004)
generate bin_0506 = conf_pen_vendor*inrange(fy,2005,2006)
generate bin_0910 = conf_pen_vendor*inrange(fy,2009,2010)
generate bin_1113 = conf_pen_vendor*inrange(fy,2011,2013)
generate bin_1415 = conf_pen_vendor*inrange(fy,2014,2015)
generate bin_1617 = conf_pen_vendor*inrange(fy,2016,2017)
generate bin_1820 = conf_pen_vendor*inrange(fy,2018,2020)
local binvars bin_0102 bin_0304 bin_0506 bin_0910 bin_1113 bin_1415 bin_1617 bin_1820
foreach y in peer_adj_ret bench_adj_upd {
	global name1 shock_event_bins_`y'
	local mode replace
	foreach fe in "fy" "ppd_id" "ppd_id fy" {
		reghdfe `y' conf_pen_vendor `binvars' $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
		test bin_0102 bin_0304 bin_0506
		local p_pre = r(p)
		test bin_0910 bin_1113
		local p_win = r(p)
		test bin_1415 bin_1617 bin_1820
		local p_post = r(p)
		outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor `binvars') ///
			addstat(Pre-shock bins = 0 p, `p_pre', Shock-period bins = 0 p, `p_win', Post-period bins = 0 p, `p_post') addtext(FE, `fe') `mode'
		local mode append
	}
	local ttl = cond("`y'"=="peer_adj_ret", "A. Peer-adjusted return", "B. Benchmark-adjusted return")
	coefplot, keep(bin_*) vertical yline(0) xline(3.5 5.5, lpattern(dash)) xlabel(, angle(45)) ///
		coeflabels(bin_0102="2001-02" bin_0304="2003-04" bin_0506="2005-06" bin_0910="2009-10" bin_1113="2011-13" bin_1415="2014-15" bin_1617="2016-17" bin_1820="2018-20") ///
		xtitle("Fiscal years (FY2007-08 = 0)") ytitle("Change in the effect of conflict") title("`ttl'", size(medium)) name(esb_`y', replace)
}
graph combine esb_peer_adj_ret esb_bench_adj_upd, ycommon rows(1) title("Event Study Around the Loglisci Shock (Two-Year Bins)", size(medium)) xsize(10) ysize(4.2)
graph export "shock_eventstudy_bins_stata.png", replace width(2400)

* =====================================================================================
* D. Differential exposure: Conflicted CIO x Shock Period with allocation interactions
* =====================================================================================
local alloc l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
tabstat l_PETotal_Actl if $samp, by(conf_pen_vendor) stat(mean)
tabstat l_PETotal_Actl if $samp & shock2==1, by(conf_pen_vendor) stat(mean)
foreach y in peer_adj_ret bench_adj_upd {
	global name1 shock_exposure_`y'
	local mode replace
	foreach fe in "fy" "ppd_id fy" {
		local ex1 ""
		local ex2 "c.l_PETotal_Actl#c.shock2"
		local ex3 "c.(`alloc')#c.shock2"
		local ex4 "c.l_PETotal_Actl#i.fy"
		local ex5 "c.(`alloc')#i.fy"
		forvalues k = 1/5 {
			reghdfe `y' conf_pen_vendor confxshock shock2 $ctl `ex`k'' if $samp, absorb(`fe') vce(cluster ppd_id fy)
			outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor confxshock) addtext(FE, `fe', Exposure spec, `k') `mode'
			local mode append
		}
	}
}

* =====================================================================================
* E. Placebo windows
* =====================================================================================
tempfile roll
capture postclose rollp
postfile rollp str20 yvar str12 fe int start double b se df using `roll', replace
foreach y in peer_adj_ret bench_adj_upd {
	foreach fe in "fy" "ppd_id fy" {
		forvalues s = 2002/2016 {
			capture drop pwin
			capture drop confxpwin
			generate pwin = inrange(fy,`s',`s'+4)
			generate confxpwin = conf_pen_vendor*pwin
			quietly reghdfe `y' conf_pen_vendor confxpwin pwin $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
			post rollp ("`y'") ("`fe'") (`s') (_b[confxpwin]) (_se[confxpwin]) (e(df_r))
		}
	}
}
postclose rollp
* fake window entirely before the shock: FY2005-2008 vs FY2001-2004, sample FY<=2008
capture drop fake
capture drop confxfake
generate fake = (fy>=2005) if fy<=2008
generate confxfake = conf_pen_vendor*fake
foreach y in peer_adj_ret bench_adj_upd {
	foreach fe in "fy" "ppd_id fy" {
		reghdfe `y' conf_pen_vendor confxfake fake $ctl if $samp & fy<=2008, absorb(`fe') vce(cluster ppd_id fy)
	}
}
preserve
use `roll', clear
list, sepby(yvar fe)
generate lo = b - invttail(df,0.025)*se
generate hi = b + invttail(df,0.025)*se
foreach y in peer_adj_ret bench_adj_upd {
	twoway (rcap lo hi start if yvar=="`y'" & fe=="ppd_id fy" & start!=2009, lcolor(gs10)) (scatter b start if yvar=="`y'" & fe=="ppd_id fy" & start!=2009, mcolor(gs10)) ///
	       (rcap lo hi start if yvar=="`y'" & fe=="ppd_id fy" & start==2009, lcolor(navy)) (scatter b start if yvar=="`y'" & fe=="ppd_id fy" & start==2009, mcolor(navy)), ///
	       yline(0) legend(off) xlabel(2002(1)2016, angle(45)) xtitle("First year of five-year window") ytitle("Conflicted CIO x Window") title("`y'", size(medium)) name(roll_`y', replace)
}
graph combine roll_peer_adj_ret roll_bench_adj_upd, ycommon rows(1) title("Placebo Windows (actual window FY2009-13 highlighted)", size(medium)) xsize(10) ysize(4.2)
graph export "shock_placebo_windows_stata.png", replace width(2400)
restore

* =====================================================================================
* F. Placebo groups: other (non-vendor, non-conflicted) departures x Shock Period
* =====================================================================================
foreach v in any_dep job_dep oth_any oth_ret oth_job oth_anyx oth_retx oth_jobx {
	capture drop `v'
}
egen any_dep = rowmax(ever_retire ever_leave_pub ever_die priv_nonam_job)
egen job_dep = rowmax(ever_leave_pub priv_nonam_job)
generate oth_any = (any_dep==1 & conf_pen_vendor==0)
generate oth_ret = (ever_retire==1 & conf_pen_vendor==0)
generate oth_job = (job_dep==1 & conf_pen_vendor==0)
foreach g in oth_any oth_ret oth_job {
	generate `g'x = `g'*shock2
}
foreach y in peer_adj_ret bench_adj_upd {
	global name1 shock_placebo_groups_`y'
	local mode replace
	foreach g in oth_any oth_ret oth_job {
		foreach fe in "fy" "ppd_id fy" {
			reghdfe `y' conf_pen_vendor confxshock `g' `g'x shock2 $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
			lincom confxshock - `g'x
			local d = r(estimate)
			local td = r(estimate)/r(se)
			outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor confxshock `g' `g'x) ///
				addstat(Conflicted x Shock minus Other x Shock, `d', t-stat, `td') addtext(FE, `fe', Other group, `g') `mode'
			local mode append
		}
	}
}
**** End shock design tests ****
