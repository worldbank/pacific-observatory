# Data 
## Sources
The study relies on two major data sources. The first is official Visitor Arrival (VA) data from the official website. There are six Pacific Islands Countries available for access: Tonga. Vanuatu, Palau, Samoa, Fiji, and Solomon Islands. Most countries mentioned above, except for Fiji, have more than 12-year monthly visitor data with countries of origin documented, suggesting more than 120 observations, which is a decent number for conducting a time series analysis.

The other is the Global Aviation Dashboard (GAD) data. The data includes the daily flight data from 2019-01-01 to up-to-date (2022-10-16) dates. Three relevant variables (number of flights, seat arrivals, and available seat kilometers) are available. All the relevant variables merely reflect the flight’s ability and do not necessarily reflect the actual onboard passengers. Since international tourism is closely related to the GDP, we mainly focus on international seat arrivals (ISA).

Given the daily frequency of GAD data and the monthly frequency of official statistics, further analysis needs to be built on the aligned frequency. Therefore, the GAD data is transformed into the monthly frequency by simply summing the whole month’s daily data. The aligned data starts from 2019-01-01 and ends at different periods varied by each available country’s latest official statistics.

Other than the abovementioned data sources, the study exploits the Google Trends data accessed from the [Development Data Partership](https://datapartnership.org/). For each country, the keyword search includes country name and suffix of "Travel," "Hotel," and "Flight," for example "Palau Travel."

## Assessment
Pearson’s correlation coefficient is an often-employed approach to test the correlation between variables. However, the employment of Pearson’s correlation could be spurious for checking the relationship between time series data because it ignores that time series data strongly depends on previous states. The additional employment of cross-correlation could be a supplement to measuring the similarity between time series data.

(Weak) stationarity is fundamental to time series analysis. Without stationarity, time series data is no different from the random walk and makes forecasting impossible. Simply put, (weak) stationarity is the basic statistical properties that do not change over time, including finite variation, constant mean, and autocovariance that only depend on the lags. The Augmented Dickey-Fuller (ADF) test is the most popular method to examine (weak) stationarity. The null hypothesis ($H_0$) is that the series is non-stationary and has a unit root. The alternative hypothesis ($H_1$) is that the series is stationary or has no unit root. Below is a summary table of the ADF tests. When the p-value is smaller than 0.05, we can reject the null hypothesis of the ADF test and conclude that the time series is stationary.  

Once achieving (weak) stationarity, the Granger causality test, which examines how useful one variable is for forecasting another variable, would make us understand whether introducing variables ISA from the Global Aviation Dashboard would help forecast the VA from the census bureau. The Granger Causality is formally expressed as:

$
VA_t = \sum_{i=1}^{p} \alpha_{i} VA_{t-i} + \sum_{i=1}^{p} \beta_{i} ISA_{t-i} + u_{t} 
$

The null hypothesis (H0) of the Granger Causality is $\beta_{i}$ = 0 for i = 1,...,p, which assumes that introducing $ISA_t$ would not help forecast $VA_t$. The nature of the Granger Causality test is VAR, which will be detailed in the Modelling section. As shown in Table 2, except for Solomon Islands, other countries pass the Granger Causality test, suggesting including ISA would help predict VA.
A general limitation of these tests is the small sample size of the available data. Despite the larger sample size of the census bureau’s data, the number of observations quickly shrinks to 44 after merging with the GAD data. The limited sample size severely affects not only the extracted information from the data but also the significance/power of the tests.
 