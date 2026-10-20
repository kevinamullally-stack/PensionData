**** Fee Ratio: spell-level Fee Slope vs. first-half/second-half comparisons ****
* Regenerates fee_slope_vs_halves.xlsx. Fee Ratio = 100 x total_fee_pct.
* Sample: CIOs who have left (curr==0) in the Table III sample.
*   A. Spell-level OLS slope of Fee Ratio on fiscal year (no allocation controls), winsorized 1/99,
*      conflicted vs. other CIOs: t-test (equal weight per spell) and regression weighted by spell
*      plan-years; by minimum spell length; medians (rank-sum test).
*   B. Mean slope by spell length.
*   C. Plan-year-weighted designs: pooled Conflicted x year trend with spell FE (and FYE FE); change
*      from first to second half within spell, conflicted vs. other departing CIOs.
*
* Run in the main do-file's data (after the Table 3 block); uses halves definitions as in
* halves_v3_fye1.do.

* --- halves and spell identifiers --------------------------------------------------------------
foreach v in last_fy max_ten ydep ten_dep second_half spell_id fee t conf_t confxsecond fee_dm m_fee {
	capture drop `v'
}
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
egen spell_id = group(cio ppd_id)
generate fee = 100*total_fee_pct
global dsamp "cio_dum==1 & fy<=2020 & curr1==0 & curr==0"
bysort fy: egen m_fee = mean(cond($dsamp, fee, .))
generate fee_dm = fee - m_fee

* =====================================================================================
* A-B. Spell-level slopes
* =====================================================================================
foreach var in fee fee_dm {
	preserve
	keep if $dsamp & !missing(`var')
	statsby slope=_b[fy] n=e(N), by(spell_id conf_pen_vendor ppd_id) clear: regress `var' fy
	drop if missing(slope)
	local mins "2 3 4 6 8"
	if "`var'"=="fee_dm" local mins "3"
	foreach k of local mins {
		display _n as text "==== `var', spells with at least `k' years ===="
		quietly _pctile slope if n>=`k', p(1 99)
		capture drop slope_w
		generate slope_w = min(max(slope, r(r1)), r(r2)) if n>=`k'
		ttest slope_w, by(conf_pen_vendor)
		regress slope_w conf_pen_vendor [aw=n], vce(cluster ppd_id)
		if inlist(`k',3,6) & "`var'"=="fee" {
			tabstat slope, by(conf_pen_vendor) stat(median n)
			ranksum slope if n>=`k', by(conf_pen_vendor)
		}
		if `k'==3 & "`var'"=="fee" {
			generate lenbin = cond(n==3,1,cond(n<=5,2,cond(n<=8,3,4)))
			label define lenbin 1 "3" 2 "4-5" 3 "6-8" 4 "9+", replace
			label values lenbin lenbin
			tabstat slope_w, by(lenbin) stat(mean n), if conf_pen_vendor==1
			tabstat slope_w, by(lenbin) stat(mean n), if conf_pen_vendor==0
		}
	}
	restore
}

* =====================================================================================
* C. Plan-year-weighted designs
* =====================================================================================
generate t = fy - 2010
generate conf_t = conf_pen_vendor*t
generate confxsecond = conf_pen_vendor*second_half
reghdfe fee conf_t t if $dsamp, absorb(spell_id) vce(cluster ppd_id fy)
reghdfe fee conf_t if $dsamp, absorb(spell_id fye1) vce(cluster ppd_id fy)
reghdfe fee second_half confxsecond if $dsamp & !missing(second_half), absorb(spell_id) vce(cluster ppd_id fy)
lincom second_half + confxsecond
reghdfe fee second_half confxsecond if $dsamp & !missing(second_half), absorb(spell_id fye1) vce(cluster ppd_id fy)
lincom second_half + confxsecond
**** End ****
