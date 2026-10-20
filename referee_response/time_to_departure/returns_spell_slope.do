**** Spell-level slope of returns: conflicted vs. other departing CIOs ****
* Regenerates returns_spell_slope.xlsx for peer_adj_ret and bench_adj_upd.
* Sample: CIOs who have left (curr==0) in the Table III sample.
* Spell-level slope = each CIO-plan spell's OLS slope of the return on fiscal year (pp per year),
* winsorized 1/99, every spell counted once (same construction as the Fee Slope).
*   A. Conflicted vs. other: by minimum spell length; net of the fiscal-year-end mean; one observation per
*      CIO; not winsorized; dropping the most negative/positive conflicted slopes.
*   B. Slope on Conflicted and the spell's first-year return and/or its own allocation-share slopes.
*   C. First-year, mean and last-year return of the same spells.
*   D. Mean slope by spell length.
*   E. Plan-year-weighted designs (spell FE) and the per-year first-to-second-half change.
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd), in the main do-file's scaled data
* (allocations already multiplied by 100).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}
foreach v in last_fy max_ten ydep ten_dep second_half spell_id eq_pct fi_pct alt_pct t conf_t confxsecond {
	capture drop `v'
}
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
egen spell_id = group(cio ppd_id)
generate eq_pct  = EQTotal_Actl
generate fi_pct  = FITotal_Actl
generate alt_pct = RETotal_Actl + PETotal_Actl + HFTotal_Actl + AltMiscTotal_Actl + COMDTotal_Actl
global t3 "cio_dum==1 & fy<=2020 & curr1==0"
global dsamp "cio_dum==1 & fy<=2020 & curr1==0 & curr==0"
* returns net of the same fiscal-year-end mean (Table III sample)
foreach y in peer_adj_ret bench_adj_upd {
	capture drop m_`y' `y'_dm
	bysort fye1: egen m_`y' = mean(cond($t3, `y', .))
	generate `y'_dm = `y' - m_`y'
}

* --- spell-level slopes: replaces the data with one row per spell (or CIO) ----------------------------
capture program drop spellslopes
program define spellslopes
	* spellslopes varlist, unit(spell|cio): s_<v> = OLS slope of <v> on fy; n = years; y0 = first-year value
	* of the first variable; requires all variables non-missing
	syntax varlist, UNIT(string)
	local y : word 1 of `varlist'
	keep if $dsamp
	foreach v of local varlist {
		keep if !missing(`v')
	}
	if "`unit'"=="cio" {
		collapse (mean) `varlist' (max) conf_pen_vendor (first) ppd_id, by(cio fy)
		local id cio
	}
	else local id spell_id
	bysort `id': generate n = _N
	bysort `id' (fy): generate y0 = `y'[1]
	bysort `id': egen mfy = mean(fy)
	generate dfy = fy - mfy
	bysort `id': egen sxx = total(dfy^2)
	foreach v of local varlist {
		bysort `id': egen sxy = total(dfy*`v')
		generate s_`v' = sxy/sxx
		drop sxy
	}
	bysort `id': egen cconf = max(conf_pen_vendor)
	bysort `id' (fy): generate pid = ppd_id[1]
	bysort `id': keep if _n==1
	keep `id' cconf pid n y0 s_*
	rename cconf conf_pen_vendor
	rename pid ppd_id
end

capture program drop slopetests
program define slopetests
	* slopetests s_var [, minobs(#) nowins drop(#) side(neg|pos)]
	syntax varname [, MINOBS(integer 3) NOWINS DROP(integer 0) SIDE(string)]
	preserve
	keep if n>=`minobs' & !missing(`varlist')
	generate d = `varlist'
	if "`nowins'"=="" {
		quietly _pctile d, p(1 99)
		replace d = min(max(d, r(r1)), r(r2))
	}
	if `drop' > 0 {
		sort conf_pen_vendor d
		if "`side'"=="neg" by conf_pen_vendor: drop if conf_pen_vendor==1 & _n<=`drop'
		if "`side'"=="pos" by conf_pen_vendor: drop if conf_pen_vendor==1 & _n>_N-`drop'
	}
	generate rising = (d>=0)
	display _n as text "==== `varlist' | min years `minobs' `nowins' | drop `drop' `side' ===="
	ttest d == 0 if conf_pen_vendor==1
	signrank d = 0 if conf_pen_vendor==1
	ttest d == 0 if conf_pen_vendor==0
	tabstat d rising, by(conf_pen_vendor) stat(mean median n)
	ttest d, by(conf_pen_vendor)
	ttest d, by(conf_pen_vendor) unequal
	ranksum d, by(conf_pen_vendor)
	regress d conf_pen_vendor [aw=n], vce(cluster ppd_id)
	restore
end

tempfile main
save `main'
foreach y in peer_adj_ret bench_adj_upd {
	* ---- A. slope tests (slopetests preserves and restores the spell-level data) ----
	use `main', clear
	spellslopes `y', unit(spell)
	foreach k in 2 3 4 6 8 {
		slopetests s_`y', minobs(`k')
	}
	slopetests s_`y', nowins
	foreach k in 3 5 {
		slopetests s_`y', drop(`k') side(neg)
		slopetests s_`y', drop(`k') side(pos)
	}
	* ---- B. mean reversion: control for the spell's first-year return ----
	keep if n>=3
	quietly _pctile s_`y', p(1 99)
	generate d = min(max(s_`y', r(r1)), r(r2))
	regress d conf_pen_vendor, vce(cluster ppd_id)
	regress d conf_pen_vendor y0, vce(cluster ppd_id)
	* ---- D. mean slope by spell length ----
	generate lenbin = cond(n==3,1,cond(n<=5,2,cond(n<=8,3,4)))
	label define lenbin 1 "3" 2 "4-5" 3 "6-8" 4 "9+", replace
	label values lenbin lenbin
	tabstat d if conf_pen_vendor==1, by(lenbin) stat(mean n)
	tabstat d if conf_pen_vendor==0, by(lenbin) stat(mean n)
	* ---- A (cont.). net of the fiscal-year-end mean; one observation per CIO ----
	use `main', clear
	spellslopes `y'_dm, unit(spell)
	slopetests s_`y'_dm
	use `main', clear
	spellslopes `y', unit(cio)
	slopetests s_`y'
	* ---- B (cont.). own allocation slopes (all four slopes winsorized 1/99) ----
	use `main', clear
	spellslopes `y' eq_pct fi_pct alt_pct, unit(spell)
	keep if n>=3
	foreach v in `y' eq_pct fi_pct alt_pct {
		quietly _pctile s_`v', p(1 99)
		replace s_`v' = min(max(s_`v', r(r1)), r(r2))
	}
	regress s_`y' conf_pen_vendor, vce(cluster ppd_id)
	regress s_`y' conf_pen_vendor s_eq_pct s_fi_pct s_alt_pct, vce(cluster ppd_id)
	regress s_`y' conf_pen_vendor y0 s_eq_pct s_fi_pct s_alt_pct, vce(cluster ppd_id)
	* ---- C. return levels of the same spells (first year, mean, last year; at least 3 years) ----
	use `main', clear
	preserve
	keep if $dsamp & !missing(`y')
	bysort spell_id (fy): generate first = `y'[1]
	bysort spell_id (fy): generate last  = `y'[_N]
	bysort spell_id: egen ybar = mean(`y')
	bysort spell_id: generate n = _N
	bysort spell_id: keep if _n==1 & n>=3
	foreach v in first ybar last {
		ttest `v', by(conf_pen_vendor)
	}
	restore
	* ---- E. plan-year-weighted designs ----
	capture drop t conf_t confxsecond
	generate t = fy - 2010
	generate conf_t = conf_pen_vendor*t
	generate confxsecond = conf_pen_vendor*second_half
	reghdfe `y' conf_t t if $dsamp, absorb(spell_id) vce(cluster ppd_id fy)
	reghdfe `y' conf_t if $dsamp, absorb(spell_id fye1) vce(cluster ppd_id fy)
	reghdfe `y' second_half confxsecond if $dsamp & !missing(second_half), absorb(spell_id) vce(cluster ppd_id fy)
	lincom second_half
	reghdfe `y' second_half confxsecond if $dsamp & !missing(second_half), absorb(spell_id fye1) vce(cluster ppd_id fy)
	* per-year first-to-second-half change, equal weight per spell
	preserve
	keep if $dsamp & !missing(second_half) & !missing(`y')
	bysort spell_id: generate n = _N
	collapse (mean) v=`y' f=fy (first) n ppd_id, by(spell_id conf_pen_vendor second_half)
	reshape wide v f, i(spell_id conf_pen_vendor n ppd_id) j(second_half)
	generate gap  = f1 - f0
	generate rate = (v1 - v0)/gap
	drop if missing(rate)
	display _n as text "==== `y' | change per year between half midpoints ===="
	tabstat gap, by(conf_pen_vendor) stat(mean n)
	ttest rate == 0 if conf_pen_vendor==0
	ttest rate, by(conf_pen_vendor)
	restore
}
use `main', clear
**** End ****
