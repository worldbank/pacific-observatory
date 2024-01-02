clear all
global folder "/Users/czhang/Desktop/pacific-observatory"

// Save the palau_merged as tempfile for merging
import delimited using "$folder/data/tourism/palau/intermediate/palau_merged.csv", 
generate time = m(2019m1) + _n-1
format time %tm
tempfile merged
save `merged'

** Merge with the Covid Stringency Index
import delimited using "$folder/data/tourism/oceania_covid_stringency.csv", clear
merge 1:1 date using `merged'
keep if _merge == 2 | _merge == 3
drop _merge v1
tempfile si
save `si'

import delimited using "$folder/data/tourism/trends/trends_palau.csv", clear
merge 1:1 date using `si'
keep if _merge != 1

** Drop the _merge variables
replace stringency_index = 0 if stringency_index == .
tsset time

** Generate Covid variable
gen covid = .
replace covid = 1 if date >= "2020m3"

** employ dfuller to test stationarity
foreach x of varlist seats_arrivals_intl total{
	dfuller `x'
}

** differencing variables
foreach x of varlist seats_arrivals_intl total{
	gen diff_`x' = d.`x'
	dfuller diff_`x'
}

** Optimal lag selection
varsoc diff_seats_arrivals_intl diff_total, maxlag(8)

** Bayes Vector Autogressive Models
bayes, rseed(17) saving($folder/bvarsim): ///
var diff_total diff_seats_arrivals_intl, lags(1/5) exog(palautravel stringency_index)

irf create var1, step(12) set($folder/scripts/notebooks/tourism/modelling/palau_irf) replace
irf graph oirf, impulse(diff_seats_arrivals_intl) response(diff_total) 
 yline(0,lcolor(black)) xlabel(0(3)12)  byopts(yrescale)
 
** Robustness Check
varstable
predict error, residual
tsline error
varlmar  // check the autocorrelation
