**** Allocations and allocation-adjusted fees: first vs. second half of tenure, each CIO weighted equally ****
* Regenerates allocations_fees_halves_equal_weight.xlsx. Same design as returns_halves_equal_weight.do.
* Sample: CIOs who have left (curr==0) in the Table III sample with defined halves.
* For each CIO-plan spell (or CIO), change = mean of the outcome in the second half minus its mean in the
* first half; conflicted vs. other departing CIOs with t-test, Welch t-test, rank-sum test, signed-rank
* test, and a regression weighting spells by plan-years. Also the spell-level slope (parallel to the Fee
* Slope).
* Outcomes: equity, fixed income, alternatives (RE + PE + HF + other alternatives + commodities), real
* estate, private equity and hedge fund shares; the Fee Ratio (100 x total_fee_pct); and the Fee Ratio net
* of allocations = residual from a pooled OLS over the Table III sample of the Fee Ratio on
*   fee_r3   : equity, fixed income and alternatives shares
*   fee_r3fe : the same three shares and fiscal-year-end date FE
*   fee_r7fe : all seven asset-class shares (cash omitted) and fiscal-year-end date FE
* The last block divides each spell's fee change by the years between its half midpoints, and regresses
* each spell's fee change (slope) on Conflicted and its own change (slope) in the three shares.
*
* Run in the main do-file's scaled data (allocations already multiplied by 100), after the Table 3 block.

foreach v in last_fy max_ten ydep ten_dep second_half spell_id {
	capture drop `v'
}
bysort cio ppd_id: egen last_fy = max(fy)
bysort cio ppd_id: egen max_ten = max(cio_tenure)
generate ydep = year_departs
replace  ydep = last_fy if missing(ydep) & curr==0
generate ten_dep = max_ten + max(ydep - last_fy, 0)
generate second_half = (cio_tenure > ten_dep/2) if !missing(cio_tenure) & !missing(ten_dep) & ten_dep>0
egen spell_id = group(cio ppd_id)
global t3 "cio_dum==1 & fy<=2020 & curr1==0"

* --- outcomes ---------------------------------------------------------------------------------------
foreach v in eq_pct fi_pct re_pct pe_pct hf_pct am_pct cm_pct alt_pct fee_ratio_pct fee_r3 fee_r3fe fee_r7fe {
	capture drop `v'
}
generate eq_pct = EQTotal_Actl
generate fi_pct = FITotal_Actl
generate re_pct = RETotal_Actl
generate pe_pct = PETotal_Actl
generate hf_pct = HFTotal_Actl
generate am_pct = AltMiscTotal_Actl
generate cm_pct = COMDTotal_Actl
generate alt_pct = re_pct + pe_pct + hf_pct + am_pct + cm_pct
generate fee_ratio_pct = 100*total_fee_pct
regress fee_ratio_pct eq_pct fi_pct alt_pct if $t3
predict fee_r3 if e(sample), resid
regress fee_ratio_pct eq_pct fi_pct alt_pct i.fye1 if $t3
predict fee_r3fe if e(sample), resid
regress fee_ratio_pct eq_pct fi_pct re_pct pe_pct hf_pct am_pct cm_pct i.fye1 if $t3
predict fee_r7fe if e(sample), resid
local outs eq_pct fi_pct alt_pct re_pct pe_pct hf_pct fee_ratio_pct fee_r3 fee_r3fe fee_r7fe
* outcomes net of the same fiscal-year-end mean (Table III sample)
foreach y of local outs {
	capture drop m_`y' `y'_dm
	bysort fye1: egen m_`y' = mean(cond($t3, `y', .))
	generate `y'_dm = `y' - m_`y'
}

capture program drop halfdiff
program define halfdiff
	* halfdiff y, unit(spell|cio) [minten(#) drop(#) side(neg|pos)]
	syntax varname, UNIT(string) [MINTEN(real 0) DROP(integer 0) SIDE(string)]
	local y `varlist'
	preserve
	keep if cio_dum==1 & fy<=2020 & curr1==0 & curr==0 & !missing(second_half) & !missing(`y') & ten_dep>=`minten'
	if "`unit'"=="spell" {
		bysort spell_id: generate n = _N
		collapse (mean) v=`y' (first) n ppd_id, by(spell_id conf_pen_vendor second_half)
		reshape wide v, i(spell_id conf_pen_vendor n ppd_id) j(second_half)
	}
	else {
		collapse (mean) v=`y' (max) conf_pen_vendor (first) ppd_id, by(cio fy second_half)
		bysort cio: generate n = _N
		bysort cio: egen cconf = max(conf_pen_vendor)
		bysort cio (fy): generate pid = ppd_id[1]
		collapse (mean) v, by(cio cconf n pid second_half)
		rename cconf conf_pen_vendor
		rename pid ppd_id
		reshape wide v, i(cio conf_pen_vendor n ppd_id) j(second_half)
	}
	generate d = v1 - v0
	drop if missing(d)
	if `drop' > 0 {
		sort conf_pen_vendor d
		if "`side'"=="neg" by conf_pen_vendor: drop if conf_pen_vendor==1 & _n<=`drop'
		if "`side'"=="pos" by conf_pen_vendor: drop if conf_pen_vendor==1 & _n>_N-`drop'
	}
	display _n as text "==== `y' | unit `unit' | min tenure `minten' | drop `drop' `side' ===="
	ttest d == 0 if conf_pen_vendor==1
	signrank d = 0 if conf_pen_vendor==1
	ttest d == 0 if conf_pen_vendor==0
	ttest d, by(conf_pen_vendor)
	ttest d, by(conf_pen_vendor) unequal
	ranksum d, by(conf_pen_vendor)
	regress d conf_pen_vendor [aw=n], vce(cluster ppd_id)
	restore
end

foreach y of local outs {
	foreach u in spell cio {
		halfdiff `y', unit(`u')
		halfdiff `y', unit(`u') minten(4)
		halfdiff `y'_dm, unit(`u')
	}
	foreach k in 3 5 {
		halfdiff `y', unit(spell) drop(`k') side(neg)
		halfdiff `y', unit(spell) drop(`k') side(pos)
		halfdiff `y', unit(cio) drop(`k') side(neg)
		halfdiff `y', unit(cio) drop(`k') side(pos)
	}
	* spell-level slope, at least 3 years, winsorized 1/99
	preserve
	keep if $t3 & curr==0 & !missing(`y')
	statsby slope=_b[fy] n=e(N), by(spell_id conf_pen_vendor ppd_id) clear: regress `y' fy
	keep if n>=3 & !missing(slope)
	quietly _pctile slope, p(1 99)
	generate slope_w = min(max(slope, r(r1)), r(r2))
	display _n as text "==== `y' | spell-level slope ===="
	ttest slope_w, by(conf_pen_vendor)
	ttest slope_w, by(conf_pen_vendor) unequal
	ranksum slope_w, by(conf_pen_vendor)
	regress slope_w conf_pen_vendor [aw=n], vce(cluster ppd_id)
	restore
}

* =====================================================================================
* Fee change per year between half midpoints; fee change (slope) on own allocation changes (slopes)
* =====================================================================================
foreach y in fee_ratio_pct fee_r3 fee_r3fe fee_r7fe {
	* per-year change
	preserve
	keep if $t3 & curr==0 & !missing(second_half) & !missing(`y')
	bysort spell_id: generate n = _N
	collapse (mean) v=`y' f=fy (first) n ppd_id, by(spell_id conf_pen_vendor second_half)
	reshape wide v f, i(spell_id conf_pen_vendor n ppd_id) j(second_half)
	generate gap  = f1 - f0
	generate rate = (v1 - v0)/gap
	drop if missing(rate)
	display _n as text "==== `y' | change per year between half midpoints ===="
	tabstat gap, by(conf_pen_vendor) stat(mean n)
	ttest rate == 0 if conf_pen_vendor==1
	signrank rate = 0 if conf_pen_vendor==1
	ttest rate == 0 if conf_pen_vendor==0
	ttest rate, by(conf_pen_vendor)
	ttest rate, by(conf_pen_vendor) unequal
	ranksum rate, by(conf_pen_vendor)
	regress rate conf_pen_vendor [aw=n], vce(cluster ppd_id)
	restore
	* halves change on Conflicted and the spell's own changes in the three shares
	preserve
	keep if $t3 & curr==0 & !missing(second_half) & !missing(`y', eq_pct, fi_pct, alt_pct)
	collapse (mean) `y' eq_pct fi_pct alt_pct (first) ppd_id, by(spell_id conf_pen_vendor second_half)
	reshape wide `y' eq_pct fi_pct alt_pct, i(spell_id conf_pen_vendor ppd_id) j(second_half)
	foreach v in `y' eq_pct fi_pct alt_pct {
		generate d_`v' = `v'1 - `v'0
	}
	display _n as text "==== `y' | halves change on Conflicted + own changes in the three shares ===="
	regress d_`y' conf_pen_vendor d_eq_pct d_fi_pct d_alt_pct, vce(cluster ppd_id)
	restore
	* spell slope on Conflicted and the spell's own slopes of the three shares (at least 3 years, winsorized 1/99)
	preserve
	keep if $t3 & curr==0 & !missing(`y', eq_pct, fi_pct, alt_pct)
	bysort spell_id: generate n = _N
	keep if n>=3
	bysort spell_id: egen mfy = mean(fy)
	generate dfy = fy - mfy
	bysort spell_id: egen sxx = total(dfy^2)
	foreach v in `y' eq_pct fi_pct alt_pct {
		bysort spell_id: egen sxy = total(dfy*`v')
		generate s_`v' = sxy/sxx
		drop sxy
	}
	bysort spell_id: keep if _n==1
	foreach v in `y' eq_pct fi_pct alt_pct {
		quietly _pctile s_`v', p(1 99)
		replace s_`v' = min(max(s_`v', r(r1)), r(r2))
	}
	display _n as text "==== `y' | spell slope on Conflicted + own slopes of the three shares ===="
	regress s_`y' conf_pen_vendor s_eq_pct s_fi_pct s_alt_pct, vce(cluster ppd_id)
	restore
}
**** End ****
