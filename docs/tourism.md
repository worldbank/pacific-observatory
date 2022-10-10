# Updates on Tourism

## EDA

Three types of data about Pacific Islands are available:
- `Available Seats Kilometers`, a variable that measures the vacancy per flight. The equation is `Available Seats` * `The number of kilometers`, however, given there is no corresponding flight distace, the variable yields little value for further analysis.

- Thus, `Number of Flights in 7 Days` and `Number of Passengers in 7 Days` become the main focus of this analysis.


## Cross-country comparisons
### Number of Flights in 7 Days

```{figure} ./images/tourism/NumFlsIn7Days.png
:name: Number of Flights in 7 Days By Country
```


And then 

<div id="content">
    <iframe src="tourism/fl.html" name="frame2" id="frame2" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>


## Statistical Properties
### Missingness

```{figure} tourism/ms_heatmap.png
:name: Missing Data Heatmap
```

Basically, from the heatmap displayed above, the missing columns `psg_wow_change` and `fl_wow_change` have exactly the same entry combinations missed. 
   
Except for **Fiji** and **Papua New Guinea**, other countries get some proportion of the missing data, ranging from 11.38% in Tuvalu to 95.14% in Solomon Islands. Noted:
- `date_range` measures difference between the first and last recorded dates;
- `df_length` is the available dataframe's length; 
- `missing` counts the missing items in the available dataframe; and 
- `available` is the true aviliable counts over the recorded time periods.


In line with missing data from the Covid Stringency Index, Fiji, Papua New Guinea, Tonga, and Solomon Islands are the countries with least missing data. A detailed count are displayed below:

- 1 out of 511 in TON is null.
- 6 out of 701 in SLB is null.
- 14 out of 957 in FJI is null.
- 14 out of 907 in PNG is null. 
- 21 out of 483 in KIR is null. 
- 21 out of 672 in VUT is null.
- 451 out of 451 in TUV is null.
- 387 out of 387 in PLW is null.
- 460 out of 460 in NRU is null.
- 859 out of 859 in MHL is null.
- 600 out of 600 in FSM is null.
- 664 out of 664 in WSM is null.

**Table 1: % Pixels with lights in the cleaned VIIRS 2021**
```{list-table}
:header-rows: 1
* - Country
  - Number of Flights Before Covid
  - Number of Flights During Covid
  - Percantage Changed 
  - Number of Passengers Before Covid
  - Number of Passengers Before Covid
  - Percentage Changed
* - Vanuatu	
  - 26.792373	
  - 29.347409	
  - 9.536430	
  - 3028.190678	
  - 2553.804223	
  - -15.66567 
* - Solomon Islands	
  - 7.199248	
  - 2.636678	
  - -63.375645	
  - 935.939850	
  - 386.366782	
  - -58.718845
* - Papua New Guinea	
  - 454.928571	
  - 465.118774	
  - 2.239957	
  - 34249.642857	
  - 32915.454662	
  - -3.895481
* - Fiji
  - 287.924051 
  - 67.417513	
  - -76.584967	
  - 26749.341772	
  - 6948.908629	
  - -74.022132
```

### Variability

## Future Directions
###  Other Data Sources

[IMF Tourism Tracker](https://www.imf.org/en/Countries/ResRep/PIS-Region) provides an estimated visitor during 2020-2021. Their method is quoted as below:
> Chinese visitors to Fiji fell by 73 percent in February relative to a year earlier. And Chinese visitors to Palau accounted for 32 percent of total visitors in 2019. Multiplying the two percentages yields the percentage point contribution to the change in visitors to Palau from Chinese visitors. Adding up the contributions across all source countries yields the total 12-month percent change.

**Regression Discontinunity in Time (RDiT)** could be especially helpful to detect the treatment effects of the Covid-19.


```