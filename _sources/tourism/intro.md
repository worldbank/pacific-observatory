# Introduction
Tourism has been a significant component of the Pacific Islands Countries (PICs) economy, driving economic growth. However, limited access to essential data and information obstructs sustainable development. For example, in the Solomon Islands, an International Finance Corporation (IFC) report estimated that tourism contributes to 10.5\% of the Gross Domestic Product (GDP) and 10.8\% of employment. [^1] Meanwhile, the latest available tourist data is from the fourth quarter of 2020, and a two-year data vacuum exists. [^2] The lagged data is not unique to the Solomon Islands, but more of a general situation for PICs.

What is worse, when Covid-19 hit globally, tourism came to a pause for PICs. Recovery slowly takes place, and data plays a more significant role in understanding how long PICs could bounce back. By leveraging alternative data sources, such as flight data, and combining them with the available historical data, we can better understand the Pacific Islands countries' economic and social conditions.

The report will be divided into five parts \[temporarily\]. The first part reviews the literature about tourism and development, specifically focusing on PICs, and the main forecasting models employed in tourism research. Then, the second part introduces the sources and features of the official and flight data and assesses their relevance by correlational and time series analysis. The third part describes the empirical modeling strategies and robustness checks. The fourth part will display the results from the model.

## Literature Review
### Tourism and Development
Several studies have examined the relationship between tourism development and PIC economic growth. 3 Seetanah (2011) examines 19 small island countries (including Fiji and Papua New Guinea), revealing that “tourism development is an important factor in explaining economic performance in island economies ... and may have comparatively higher growth effects.” Narayan et. al exploit the panel data for four PICs (Fiji, Tonga, Solomon Islands, and Papua New Guinea) and finds that “a 1% increase in tourism exports increases GDP by 0.72% in the long run and by 0.24% in the short run.” A recent study by Kumar and Stauvermann (2021) focused on Fiji, Samoa, Solomon Islands, Tonga, and Vanuatu reveals the same result that tourism development is growth-enhancing for all five countries.

### Forecast 
Most tourism models employed in tourism forecasting can be classified as time series, econometric, and artificial neural network (ANN) models. Time series models are based on historical patterns, and the AutoRegressive (AR) model is the fundamental one. To fully absorb the forecasting error, Moving Average (MA) model is often combined with the AR model, constructing an ARMA model. Including Seasonality and differencing would increase the forecasting accuracy and leads to the SARIMA model. Considering the causes and effects of tourism, the econometric model often includes exogenous variables and results in a multivariate analysis.

The classical one is the Vector AR (VAR) model, which assumes that “all of the variables affect each other intertemporally”. Despite the ANN model’s performance, the ”black box” model and requirement of a large amount of data makes ANN incompatible with the limited data we have.

Turning to the indicator, visitor arrivals have been key in checking the tourism industry and modeling macroeconomic growth. Built on the assumption that visitor arrivals by the departure countries could have similar patterns for PICs under Covid-19, International Monetary Fund (IMF) utilizes Fiji’s official monthly tourism data, which had a quick turnaround of about 19 days, and produces the estimates of visitor arrivals for other PICs, helping monitor the tourism industry when timely data was not available. Other than the monitoring, total visitor arrivals are often employed as the proxies of tourism expansions and inserted into the equation along with Foreign Direct Investment (FDI), remittances, and other variables to model economic growth.

### Forecast Combination
Beyond the individual forecast, recent studies have combined multiple models to improve forecasting accuracy (Wong et al. 2007). As Timmermann (2006) reviews, forecast combinations have, on average, outperformed the single best forecasts, with the evidence from M-3 Competition and Stock and Watson (2004). The explanations behind the superiority of combination are
mainly from “incorporat\[ing\] partial (but incompletely overlapping) information” and mitigating the structural breaks and instabilities with varying degrees of misspecification and adaptability
(Wang et al. 2022, p. xxx).

In terms of the combination schemes, they can be linear or non-linear, static or time-varying, series-specific or cross-learning, and consider or ignore correlations among individual forecasts(Wang et al. 2022). However, simple averaging often dominates the sophisticated weighting schemes, the phenomenon called “forecasting combination puzzle.”


[^1]: https://www.ifc.org/wps/wcm/connect/region__ext_content/ifc_external_corporate_site/east+asia+and+the+pacific/resources/solomon+islands+tourism+industry+guides+for+investors+and+government
[^2]: See more in https://www.statistics.gov.sb/statistics/visitor-arrivals#month
