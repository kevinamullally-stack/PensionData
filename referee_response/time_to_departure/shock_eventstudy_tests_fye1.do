**** Event studies around the Loglisci shock: shock-period vs. non-shock coefficients ****
* Regenerates shock_eventstudy_tests_fye1.xlsx. Two event studies (single years with FY2008 base;
* two-year bins with FY2007-08 base), each with (1) fiscal-year-end date FE and (2) plan and
* fiscal-year-end date FE, for peer_adj_ret and bench_adj_upd.
*
* The average effect of conflict in a group of years = Conflicted CIO + the average of that group's
* interaction coefficients, weighting each coefficient by the fiscal years it covers in the
* FY2002-2020 regression sample and counting the base period as zero (so the tests do not depend on
* the base period). Shock-period years: FY2009-2013. Non-shock years: FY2002-2008 and FY2014-2020.
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
global ctl $controls1 $controls2 $controls3 $controls4 $controls5
global samp "cio_dum==1 & curr1==0 & fy<=2020"

* --- event indicators ----------------------------------------------------------------------
capture drop es_*
capture drop bin_*
generate es_pre  = conf_pen_vendor*(fy<2005)          // FY2002-2004 in the regression sample (3 years)
generate es_post = conf_pen_vendor*(fy>2017)          // FY2018-2020 (3 years)
local esvars "es_pre"
forvalues t = 2005/2017 {
	if `t' != 2008 {
		generate es_`t' = conf_pen_vendor*(fy==`t')
		local esvars "`esvars' es_`t'"
	}
}
local esvars "`esvars' es_post"
generate bin_0102 = conf_pen_vendor*inrange(fy,2001,2002)   // FY2002 only in the regression sample
generate bin_0304 = conf_pen_vendor*inrange(fy,2003,2004)
generate bin_0506 = conf_pen_vendor*inrange(fy,2005,2006)
generate bin_0910 = conf_pen_vendor*inrange(fy,2009,2010)
generate bin_1113 = conf_pen_vendor*inrange(fy,2011,2013)
generate bin_1415 = conf_pen_vendor*inrange(fy,2014,2015)
generate bin_1617 = conf_pen_vendor*inrange(fy,2016,2017)
generate bin_1820 = conf_pen_vendor*inrange(fy,2018,2020)
local binvars bin_0102 bin_0304 bin_0506 bin_0910 bin_1113 bin_1415 bin_1617 bin_1820

* --- year-weighted means of the interaction coefficients (base period = 0) --------------------
* single years
local s_shock "(es_2009 + es_2010 + es_2011 + es_2012 + es_2013)/5"
local s_pre   "(3*es_pre + es_2005 + es_2006 + es_2007)/7"
local s_post  "(es_2014 + es_2015 + es_2016 + es_2017 + 3*es_post)/7"
local s_non   "(3*es_pre + es_2005 + es_2006 + es_2007 + es_2014 + es_2015 + es_2016 + es_2017 + 3*es_post)/14"
* two-year bins
local b_shock "(2*bin_0910 + 3*bin_1113)/5"
local b_pre   "(bin_0102 + 2*bin_0304 + 2*bin_0506)/7"
local b_post  "(2*bin_1415 + 2*bin_1617 + 3*bin_1820)/7"
local b_non   "(bin_0102 + 2*bin_0304 + 2*bin_0506 + 2*bin_1415 + 2*bin_1617 + 3*bin_1820)/14"

foreach es in s b {
	if "`es'"=="s" local ev `esvars'
	else           local ev `binvars'
	foreach y in peer_adj_ret bench_adj_upd {
		global name1 shock_es_tests_`es'_`y'
		local mode replace
		foreach fe in "fye1" "ppd_id fye1" {
			reghdfe `y' conf_pen_vendor `ev' $ctl if $samp, absorb(`fe') vce(cluster ppd_id fy)
			* average effect of conflict in each group of years
			foreach g in shock non pre post {
				lincom conf_pen_vendor + ``es'_`g''
				local L_`g' = r(estimate)
			}
			* differences, with t and p
			lincom ``es'_shock' - ``es'_non'
			local d_non = r(estimate)
			local t_non = r(estimate)/r(se)
			local p_non = r(p)
			lincom ``es'_shock' - ``es'_pre'
			local d_pre = r(estimate)
			local t_pre = r(estimate)/r(se)
			local p_pre = r(p)
			lincom ``es'_shock' - ``es'_post'
			local d_post = r(estimate)
			local t_post = r(estimate)/r(se)
			local p_post = r(p)
			outreg2 using $name1, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) keep(conf_pen_vendor `ev') ///
				addstat(Avg effect shock years, `L_shock', Avg effect non-shock years, `L_non', Shock minus non-shock, `d_non', t, `t_non', p, `p_non', ///
				        Avg effect pre-shock years, `L_pre', Avg effect post-shock years, `L_post', Shock minus pre-shock, `d_pre', t, `t_pre', p, `p_pre', Shock minus post-shock, `d_post', t, `t_post', p, `p_post') ///
				addtext(FE, `fe') `mode'
			local mode append
		}
	}
}
**** End ****
