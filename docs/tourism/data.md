# Data

## Sources

The study relies on two primary data sources. The first is official Visitor Arrival (VA) data from official websites. Six Pacific Islands Countries have official data available for access: Fiji, Palau, Samoa, Solomon Islands, Tonga, and Vanuatu. All countries, except for Fiji, have more than 12 years of monthly visitor data with countries of origin documented, resulting in more than 120 observations for modeling.

4 The other is the Global Aviation Dashboard (GAD) data, which includes daily flight data from January 2019 to the current date (October 2022 for this study). Three relevant variables are available: number of flights, seat arrivals, and available seat kilometers. These variables reflect the flight’s ability and do not necessarily reflect the occupancy rates or onboard passengers. Since the number of visitors is closely related to economic output, we mainly focus on international seat arrivals (ISA).

Given the daily frequency of GAD data and the monthly frequency of official statistics, we align both datasets to the same frequency for further analysis. We transform the GAD data into monthly frequency by summing daily entries of the same month. The aligned data starts on 2019-01-01 and ends at different periods, depending on each country’s latest official data.

Besides the abovementioned data sources, the study incorporates the Google Trends data from the World Bank’s [Development Data Partership](https://datapartnership.org/). For each country, we conducted a keyword search, including the country name and suffix of “travel,” “hotel,” and “flight,” for example, “Palau travel.” [1]

## Assessment

As seen in Figure 1, the orange line represents the GAD’s ISA, and the blue line represents the VA data. VA and ISA typically moved together, except for months following the announcement of Covid-19 as a global pandemic. Beyond the rough observation, a series of assessments are conducted, including correlation, stationarity, and Granger Causality analyses.

Pearson’s correlation coefficient is an often-employed approach to test the correlation between variables. However, the employment of Pearson’s correlation could be spurious because it ignores that time series data strongly depends on previous states. Cross-correlation is essential to measuring the similarity between two time series.

Weak stationarity is fundamental to time series analysis. Time series data is no different from random walks without stationarity, making forecasting impossible. Simply put, weak stationarity is the principle that basic statistical properties do not change over time, including finite variation, constant mean, and autocovariance that only depends on lags. The Augmented Dickey-Fuller (ADF) test is the most commonly employed method to examine weak stationarity. The null hypothesis ($H_0$) is that the series is non-stationary and has a unit root. The alternative hypothesis ($H_1$) is that the series is stationary or has no unit root. Below is a summary table of the ADF tests.


Pearson’s correlation coefficient is an often-employed approach to test the correlation between variables. However, the employment of Pearson’s correlation could be spurious for checking the relationship between time series data because it ignores that time series data strongly depends on previous states. The additional employment of cross-correlation could be a supplement to measuring the similarity between time series data.

(Weak) stationarity is fundamental to time series analysis. Without stationarity, time series data is no different from the random walk and makes forecasting impossible. Simply put, (weak) stationarity is the basic statistical properties that do not change over time, including finite variation, constant mean, and autocovariance that only depend on the lags. The Augmented Dickey-Fuller (ADF) test is the most popular method to examine (weak) stationarity. The null hypothesis ($H_0$) is that the series is non-stationary and has a unit root. The alternative hypothesis ($H_1$) is that the series is stationary or has no unit root. Below is a summary table of the ADF tests. When the p-value is smaller than 0.05, we can reject the null hypothesis of the ADF test and conclude that the time series is stationary.  

Once achieving (weak) stationarity, the Granger causality test, which examines how useful one variable is for forecasting another variable, would make us understand whether introducing variables ISA from the Global Aviation Dashboard would help forecast the VA from the census bureau. The Granger Causality is formally expressed as:

$
VA_t = \sum_{i=1}^{p} \alpha_{i} VA_{t-i} + \sum_{i=1}^{p} \beta_{i} ISA_{t-i} + u_{t} 
$

The null hypothesis (H0) of the Granger Causality is $\beta_{i}$ = 0 for i = 1,...,p, which assumes that introducing $ISA_t$ would not help forecast $VA_t$. The nature of the Granger Causality test is VAR, which will be detailed in the Modelling section. As shown in Table 2, except for Solomon Islands, other countries pass the Granger Causality test, suggesting including ISA would help predict VA.
A general limitation of these tests is the small sample size of the available data. Despite the larger sample size of the census bureau’s data, the number of observations quickly shrinks to 44 after merging with the GAD data. The limited sample size severely affects not only the extracted information from the data but also the significance/power of the tests.
 