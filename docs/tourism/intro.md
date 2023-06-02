# Introduction

Tourism has been a significant component of the Pacific Islands Countries (PICs) economy, driving economic growth. However, limited access to essential data and information obstructs sustainable development. For example, in the Solomon Islands, an International Finance Corporation (IFC) report estimated that tourism contributes to 10.5\% of the Gross Domestic Product (GDP) and 10.8\% of employment. [^1] Meanwhile, the latest available tourist data is from the fourth quarter of 2020, and a two-year data vacuum exists. [^2] The lagged data is not unique to the Solomon Islands, but more of a general situation for PICs.

What is worse, when Covid-19 hit globally, tourism came to a pause for PICs. Recovery slowly takes place, and data plays a more significant role in understanding how long PICs could bounce back. By leveraging alternative data sources, such as flight data, and combining them with the available historical data, we can better understand the Pacific Islands countries' economic and social conditions.

The report will be divided into five parts \[temporarily\]. The first part reviews the literature about tourism and development, specifically focusing on PICs, and the main forecasting models employed in tourism research. Then, the second part introduces the sources and features of the official and flight data and assesses their relevance by correlational and time series analysis. The third part describes the empirical modeling strategies and robustness checks. The fourth part will display the results from the model.

## Literature Review

### Tourism and Growth
Tourism has been recognized as a key driver of economic growth in developing countries. {cite:t}`seetanah2011assessing` examines 19 island economies, reveals a bi-causal relationship between tourist and growth, and confirms the fact that "tourism development on island economies may have comparatively higher growth effects."
 
Tourism has emerged as a crucial catalyst for economic development. {cite:t}`narayan2013does` found that a 1% increase in tourism exports leads to a 0.72% long-term increase in GDP and a 0.24% short-term increase in Pacific Islands countries. {cite:t}`kumar2021tourism` focused specifically on Fiji, Samoa, Solomon Islands, Tonga, and Vanuatu and found that tourism development is growth-enhancing for all five countries. These studies collectively provide compelling evidence of the significant contribution of tourism to economic growth and development in Pacific Islands countries.

### Indicators

Visitor arrivals play a pivotal role in the evaluation of the tourism industry and the projection of macroeconomic growth. In the context of PICs during the Covid-19 pandemic, it is hypothesized that visitor arrivals from departure countries exhibit similar patterns. Leveraging this assumption, the International Monetary Fund (IMF) utilizes Fiji's official monthly tourism data, which boasts a rapid turnaround time of approximately 19 days. This data is employed to estimate visitor arrivals for other PICs, thereby facilitating the monitoring of the tourism industry when timely data is scarce. 

Other than the visitor arrivals, 

### Forecast

Most tourism models employed in tourism forecasting can be classified as time series, econometric, and artificial neural network (ANN) models. Time series models are based on historical patterns, and the AutoRegressive (AR) model is the fundamental one. To fully absorb the forecasting error, Moving Average (MA) model is often combined with the AR model, constructing an ARMA model. Including Seasonality and differencing would increase the forecasting accuracy and leads to the SARIMA model. Considering the causes and effects of tourism, the econometric model often includes exogenous variables and results in a multivariate analysis.

The classical one is the Vector AR (VAR) model, which assumes that “all of the variables affect each other intertemporally”. Despite the ANN model’s performance, the ”black box” model and requirement of a large amount of data makes ANN incompatible with the limited data we have.

### Forecast Combination

Beyond the individual forecast, there has been a trend to combine individual forecasts to improve accuracy. As {cite:ts}`timmermann2006forecast` reviews, forecast combinations have, on average, outperformed the single best forecasts, with the evidence from [M-3 Competition](https://forecasters.org/resources/time-series-data/m3-competition/) and {cite:ts}`stock1998comparison`. The explanations behind the superiority of combination are mainly from “incorporat\[ing\] partial (but incompletely overlapping) information” and mitigating the structural breaks and instabilities with varying degrees of misspecification and adaptability {cite:ps}`wang2022forecast`. 

In terms of the combination schemes, they can be linear or non-linear, static or time-varying, series-specific or cross-learning, and consider or ignore correlations among individual forecasts {cite:ps}`wang2022forecast`. The most straightforward one is the equally weighted average method, which can be easily implemented by calculating the simple arithmetic average of forecasts. Despite ignoring the precision of individual forecasts and correlations between errors, the method often works well compared to complex combination schemes, the phenomenon called “forecasting combination puzzle.”

The linear combination scheme is built on the idea that greater weights should be assigned to the most accurate forecast method. The exemplary one is relative performance weights, which are based on each model’s relative MSE performance. Least-square estimator of the weights was introduced by {cite:ts}`granger1984improved`. In the seminal work, they recommended that weights can be estimated by the ordinary least squares (OLS) with past observations as the response variable and individual forecasts as the predictor variables. Researchers also relate the combination estimation to the shrinkage methods, aiming to strike a balance between information and noise/bias from individual forecasts or solving the estimation uncertainty under N>T, such as LASSO.

Despite that forecast combinations captured numerous attentions from 1980s, only 17 of a pool of 211 tourism studies involve the forecast combination, and most of them were conducted in late 2000s, like  {cite:ps}`wong2007tourism`.

[^1]: <https://www.ifc.org/wps/wcm/connect/region__ext_content/ifc_external_corporate_site/east+asia+and+the+pacific/resources/solomon+islands+tourism+industry+guides+for+investors+and+government>
[^2]: See more in <https://www.statistics.gov.sb/statistics/visitor-arrivals#month>
