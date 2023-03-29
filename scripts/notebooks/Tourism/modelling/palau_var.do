clear all
global folder "/Users/czhang/Desktop/pacific-observatory"

// Save the palau_merged as tempfile for merging
import delimited using "$folder/data/tourism/palau/intermediate/palau_merged.csv", 
generate time = m(2019m1) + _n-1
format time %tm
tempfile merged
save `merged'

// Merge with the Covid Stringency Index
import delimited using "$folder/data/tourism/oceania_covid_stringency.csv", clear
merge 1:1 date using `merged'
keep if _merge == 2 | _merge == 3

// Drop the _merge variables
drop _merge v1
replace stringency_index = 0 if stringency_index == .
tsset time

// employ dfuller to test stationarity
foreach x of varlist seats_arrivals_intl-total{
	dfuller `x'
}

// Vector Autogressive Models
var total seats_arrivals_intl, exog(stringency_index)
