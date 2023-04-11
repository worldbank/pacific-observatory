# Introduction
Tourism has been a significant component of the Pacific Islands Countries (PICs) economy, driving economic growth. However, limited access to essential data and information obstructs sustainable development. For example, in the Solomon Islands, an International Finance Corporation (IFC) report estimated that tourism contributes to 10.5\% of the Gross Domestic Product (GDP) and 10.8\% of employment.[^1] Meanwhile, the latest available tourist data is from the fourth quarter of 2020, and a two-year data vacuum exists. [^2] The lagged data is not unique to the Solomon Islands, but more of a general situation for PICs.

What is worse, when Covid-19 hit globally, tourism came to a pause for PICs. Recovery slowly takes place, and data plays a more significant role in understanding how long PICs could bounce back. By leveraging alternative data sources, such as flight data, and combining them with the available historical data, we can better understand the Pacific Islands countries' economic and social conditions.

The report will be divided into five parts [temporarily]. The first part reviews the literature about tourism and development, specifically focusing on PICs, and the main forecasting models employed in tourism research. Then, the second part introduces the sources and features of the official and flight data and assesses their relevance by correlational and time series analysis. The third part describes the empirical modeling strategies and robustness checks. The fourth part will display the results from the model.

## Literature Review
### Tourism and Development
Several studies have examined the relationship between tourism development and PIC economic growth. 3 Seetanah (2011) examines 19 small island countries (including Fiji and Papua New Guinea), revealing that “tourism development is an important factor in explaining economic performance in island economies ... and may have comparatively higher growth effects.” Narayan et al. exploit the panel data for four PICs (Fiji, Tonga, Solomon Islands, and Papua New Guinea) and finds that “a 1% increase in tourism exports increases GDP by 0.72% in the long run and by 0.24% in the short run.” A recent study by Kumar and Stauvermann (2021) focused on Fiji, Samoa, Solomon Islands, Tonga, and Vanuatu reveals the same result that tourism development is growth-enhancing for all five countries.

### Tourism Forecasting
Most tourism models employed in tourism forecasting can be classified as time series, econometric, and artificial neural network (ANN) models. Time series models are based on historical patterns, and the AutoRegressive (AR) model is the fundamental one. To fully absorb the forecasting error, Moving Average (MA) model is often combined with the AR model, constructing an ARMA model. Including Seasonality and differencing would increase the forecasting accuracy and leads to the SARIMA model. Considering the causes and effects of tourism, the econometric model often includes exogenous variables and results in a multivariate analysis.

The classical one is the Vector AR (VAR) model, which assumes that “all of the variables affect each other intertemporally”. Despite the ANN model’s performance, the ”black box” model and requirement of a large amount of data makes ANN incompatible with the limited data we have.

Turning to the indicator, visitor arrivals have been key in checking the tourism industry and modeling macroeconomic growth. Built on the assumption that visitor arrivals by the departure countries could have similar patterns for PICs under Covid-19, International Monetary Fund (IMF) utilizes Fiji’s official monthly tourism data, which had a quick turnaround of about 19 days, and produces the estimates of visitor arrivals for other PICs, helping monitor the tourism industry when timely data was not available. Other than the monitoring, total visitor arrivals are often employed as the proxies of tourism expansions and inserted into the equation along with Foreign Direct Investment (FDI), remittances, and other variables to model economic growth.

## Data 
### Sources
The study relies on two distinct kinds of data sources. The first is official Visitor Arrival (VA) data from the official website. There are six Pacific Islands Countries available for access: Tonga. Vanuatu, Palau, Samoa, Fiji, and Solomon Islands. Most countries mentioned above, except for Fiji, have more than 12-year monthly visitor data with countries of origin documented, suggesting more than 120 observations, which is a decent number for conducting a time series analysis.

The other is the Global Aviation Dashboard (GAD) data. The data includes the daily flight data from 2019-01-01 to up-to-date (2022-10-16) dates. Three relevant variables (number of flights, seat arrivals, and available seat kilometers) are available. All the relevant variables merely reflect the flight’s ability and do not necessarily reflect the actual onboard passengers. Since international tourism is closely related to the GDP, we mainly focus on international seat arrivals (ISA).

Given the daily frequency of GAD data and the monthly frequency of official statistics, further analysis needs to be built on the aligned frequency. Therefore, the GAD data is transformed into the monthly frequency by simply summing the whole month’s daily data. The aligned data starts from 2019-01-01 and ends at different periods varied by each available country’s latest official statistics.



<div id="content">
    <iframe src="interactive/tourism/tourism-psg.html" name="flights" id="flights" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>


### Assessment

```{figure} tourism/ms_heatmap.png
:name: Missing Data Heatmap
```

## Empirical Modelling
Built on the previous tourism research, a Seasonal Auto-Regressive Integrated Moving Average with eXogenous factors (SARIMAX) model would be employed to track each PIC's VAs. A SARIMAX model consists of three elements: AR, MA, and X. The AR part of the model use the past values of the differenced series to make predictions, while the MA part uses the past errors of the model. An SARIMAX $(p,d,q)(P,D,Q,s)$ is defined as below:
\begin{equation*}
\centering
\Theta(L)^{p} \theta(L^{s})^{P} \Delta^{d} \Delta_{s}^{D} VA_{t} = \Phi(L)^{q} \phi(L^{s})^{Q} \Delta^{d} \Delta_{s}^{D} \epsilon_{t} + \sum_{i=1}^{n} \beta_{i} {x}_{t}^{i}
\end{equation*}
where: 
\begin{itemize}
    \singlespacing
    \item ${VA}_{t}$ is the Visitor Arrivals at time $t$
    \item ${x}_{t}^{i}$ for $i <= n$ with coefficients $\beta_{i}$ denotes $n$
 exogenous variables defined at each time step $t$
    \item $L$ is the lag operator and $L^{s}$ is the seasonal lag operator 
    \item $p$ is the order of the AR part, $q$ is the order of the MA part, and $d$ is the degree of first differencing involved
    \item $\Theta(L)^{p}$ is an order $p$ polynomial function of $L$ from the AR part, and $\phi$ is defined analogously to $\Theta$.
    \item $\Delta^{d}$ is the integration operator and $\Delta_{s}^{D}$ takes the seasonal differences of the series
\end{itemize}
The model employs the scaled logit transformation to avoid negative predictions, transforming $x$ to $\log(\frac{x-a}{b-x})$, where $a$ is the lower bound and $b$ is the upper bound. Further, to prevent -$\infty$, $a$ is set to be slightly smaller than the minimum of the series, and $b$ is slightly larger than the maximum. 


[^1]: 
[^2] See more in https://www.statistics.gov.sb/statistics/visitor-arrivals#month.