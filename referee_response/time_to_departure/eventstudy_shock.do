**** Table 5b event study around the Loglisci shock: peer- and benchmark-adjusted returns ****
* Same specification as the Table 5b block of ConflictedCIOs_8Oct2025.do, run for peer_adj_ret and
* bench_adj_upd (PPD return minus the updated benchmark: reported, else inferred grade A/B).
* Regenerates eventstudy_shock_tables.xlsx and eventstudy_shock_peer_bench.png.
* Adds a test that the pre-period coefficients are equal to each other.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd). Requires coefplot (ssc install coefplot).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}

* control globals in effect at Table 5b in the main do-file
global controls1 l_investmentreturn_1yr size l_ActFundedRatio_GASB
global controls2 l_EQTotal_Actl l_FITotal_Actl l_RETotal_Actl l_PETotal_Actl l_HFTotal_Actl l_AltMiscTotal_Actl l_COMDTotal_Actl l_CashTotal_Actl
global controls3 fincenter1
global controls4 l_log_cio_age l_log_cio_tenure
global controls5 l_sib1 wstate_political

local baseyr    2009
local prestart  2005
local postend   2017

cap drop pre_bin post_bin
gen pre_bin  = conf_pen_vendor * (fy < `prestart')
gen post_bin = conf_pen_vendor * (fy > `postend')
label var pre_bin  "Conflicted CIO x FY<`prestart'"
label var post_bin "Conflicted CIO x FY>`postend'"
local eventvars "pre_bin"
local prevars   "pre_bin"
local postvars  "post_bin"
local flat ""
local clab ""
forvalues yr = `prestart'/`postend' {
	if `yr' != `baseyr' {
		cap drop conf_yr_`yr'
		gen conf_yr_`yr' = conf_pen_vendor * (fy == `yr')
		label var conf_yr_`yr' "Conflicted CIO x FY`yr'"
		local eventvars "`eventvars' conf_yr_`yr'"
		local clab `"`clab' conf_yr_`yr' = "`yr'""'
		if `yr' < `baseyr' local prevars  "`prevars' conf_yr_`yr'"
		if `yr' > `baseyr' local postvars "`postvars' conf_yr_`yr'"
	}
}
local eventvars "`eventvars' post_bin"
* pre-period equal: pre_bin = 2005 = 2006 = 2007 = 2008 (each against FY2008)
foreach v of local prevars {
	if "`v'"!="conf_yr_2008" local flat "`flat' (`v' = conf_yr_2008)"
}

local glist ""
foreach y in peer_adj_ret bench_adj_upd {
	global name3 eventstudy_shock_`y'
	local mode replace
	foreach fe in "fy" "ppd_id" "ppd_id fy" {
		reghdfe `y' `eventvars' $controls1 $controls2 $controls3 $controls4 $controls5 ///
			if cio_dum==1 & curr1==0 & fy<=2020, absorb(`fe') vce(cluster ppd_id fy)
		test `prevars'
		local p_pre = r(p)
		test `flat'
		local p_flat = r(p)
		test `postvars'
		local p_post = r(p)
		outreg2 using $name3, excel stats(coef tstat) alpha(0.01, 0.05, 0.1) symbol(***, **, *) nonotes tdec(2) rdec(3) bdec(3) ///
			keep(`eventvars') addstat(Adj. R-squared, e(r2_a), Pre-period jointly zero p, `p_pre', Pre-period equal p, `p_flat', Post-period jointly zero p, `p_post') ///
			addtext(FE, `fe') `mode'
		local mode append
	}
	* plot from the plan + year FE specification (the last one estimated); the dashed line marks the omitted FY2009
	local ttl = cond("`y'"=="peer_adj_ret", "A. Peer-adjusted return", "B. Benchmark-adjusted return (updated benchmark)")
	coefplot, keep(conf_yr_*) vertical yline(0) xline(4.5, lpattern(dash)) ///
		xtitle("Fiscal year (FY`baseyr' = 0)") ytitle("Conflicted CIO x Year coefficient") ///
		title("`ttl'", size(medium)) xlabel(, angle(45)) ///
		coeflabels(`clab') name(es_`y', replace)
	graph export "eventstudy_shock_`y'.png", replace width(2400)
	local glist "`glist' es_`y'"
}
graph combine `glist', ycommon rows(1) title("Event Study: Conflicted CIO Performance Around the Loglisci Shock", size(medium)) xsize(10) ysize(4.2)
graph export "eventstudy_shock_peer_bench_stata.png", replace width(2400)
**** End event study ****
