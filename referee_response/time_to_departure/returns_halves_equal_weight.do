**** Returns: first vs. second half of tenure, each CIO weighted equally ****
* Regenerates returns_halves_equal_weight.xlsx for peer_adj_ret and bench_adj_upd.
* Sample: CIOs who have left (curr==0) in the Table III sample with defined halves.
* For each CIO-plan spell (or CIO), change = mean return in the second half minus mean in the first
* half; conflicted vs. other departing CIOs with t-test, Welch t-test, rank-sum test, signed-rank test,
* and a regression weighting spells by plan-years. Also the spell-level return slope (parallel to the
* Fee Slope).
*
* Run AFTER updated_benchmark_tables.do (creates bench_adj_upd).

capture confirm variable bench_adj_upd
if _rc {
	display as error "run updated_benchmark_tables.do first (it creates bench_adj_upd)"
	exit 111
}
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
* returns net of the same fiscal-year-end mean (Table III sample)
foreach y in peer_adj_ret bench_adj_upd {
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

foreach y in peer_adj_ret bench_adj_upd {
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
	* spell-level return slope, at least 3 years, winsorized 1/99
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
**** End ****
