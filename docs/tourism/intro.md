# Introduction

Tourism represents a significant component of the Pacific Islands Countries (PICs) economy and an important driver of economic growth. However, limited access to essential data and information obstructs informed policy on tourism. For example, an International Finance Corporation (IFC) report on the Solomon Islands estimated that tourism contributes 10.5% of the Gross Domestic Product (GDP) and 10.8% of employment.(IFC 2021) Meanwhile, the latest available data on tourist visitors are from the fourth quarter of 2020, and a two-year data vacuum exists. The lagged data is not unique to the Solomon Islands, but is representative of a general trend for PICs.

What is worse, tourism in the PICs came to a halt during the Covid-19 pandemic. As the islands continue to reopen doors, data plays a role in monitoring the recovery of the tourism sector in the PICs. By leveraging alternative data sources, such as flight data, and combining them with the available historical data, we can better understand the economic well-being of this region in the post-pandemic era.

The report will be divided into five sections. The first section reviews the tourism and development literature, specifically focusing on major forecasting approaches employed in tourism research. The second section introduces the data sources and features of the official and flight data and assesses their relevance using correlational analysis. The third section describes the empirical modeling strategies and robustness checks. The fourth section presents the results from various time-series models. The last section discusses the implications and limitations of the methods presented.

## Literature Review

### Tourism and Economic Growth

Tourism has been recognized as a critical driver of economic growth in developing countries. As {cite:t}`brida2016has` show in their exhaustive review of approximately 100 journal articles on tourism, the tourism-led growth hypothesis has been supported by most studies with a few exceptions. {cite:t}`seetanah2011assessing` examined 19 island economies, revealing a bi-causal relationship between tourism and growth and concluding that “tourism development on island economies may have comparatively higher growth effects.”

{cite:t}`narayan2013does` found that a 1% increase in tourism exports leads to a 0.72% long-term increase in GDP and a 0.24% short-term increase in the PICs. Kumar and Stauvermann (2021) explicitly focused on Fiji, Samoa, Solomon Islands, Tonga, and Vanuatu and found that tourism development is growth-enhancing for all five countries. An earlier article by {cite:t}`narayan2004fiji` found that “growth in income in Fiji’s main tourist source markets [New Zealand, Australia, and the US] has a positive impact on visitor arrivals.” These studies collectively provide compelling evidence of the significant contribution of tourism to economic growth and development in PICs.

### Forecast

Tourism forecasting has been fundamental to tourism research and management, and various approaches have been used to generate the forecasts. As {cite:t}`song2019review` suggest, most tourism forecasts fall into four categories: time series, econometric, artificial-intelligence-based (AI-based), and judgmental models. Time series models forecast based on historical patterns, econometric models focus on causes and effects of economic factors on tourism, and AI-based models take advantage of the recent advancements in deep neural networks.

2 Beyond individual forecasts, there has been a trend to combine individual forecasts to improve accuracy. As {cite:t}`timmermann2006forecast` reviews, forecast combinations have, on average, outperformed the single best forecasts, with the evidence from [M-3 Competition](https://forecasters.org/resources/time-series-data/m3-competition/) {cite:p}`stock1998comparison`. Forecasts based on the combination could “incorporate partial (but incompletely overlapping) information” and mitigate the structural breaks and instabilities with varying degrees of misspecification and adaptability {cite:p}`wang2022forecast`. Even though the forecast combination has captured broad attention since the 1980s, only 17 of 211 tourism studies used this approach, most of them in the late 2000s, like Wong et al. (2007).

The combination schemes can be linear or non-linear, static or time-varying, series-specific or cross-learning, and consider or ignore correlations among individual forecasts {cite:p}`wang2022forecast`. The most straightforward one is the equally weighted average method, which can be easily implemented by calculating the simple arithmetic average of forecasts. Despite ignoring the precision of individual forecasts and correlations between errors, the method often works well compared to complex combination schemes, the phenomenon called “forecasting combination puzzle.”

The linear combination scheme is built on the idea that greater weights should be assigned to the most accurate forecast method. An intuitive method is relative performance weights, which are assigned based on each model’s mean squared error (MSE). The least-square estimator of the weights was introduced by {cite:ts}`granger1984improved`. They recommended that weights be estimated by the ordinary least squares (OLS) with past observations as the response variable and individual forecasts as the predictor variables. Researchers also relate the combination estimation to shrinkage methods, aiming to balance information and noise/bias from individual forecasts, such as LASSO- and Ridge- procedures by {cite:ts}`diebold2019machine`.

### Tourism Data

Recent studies have taken advantage of big data generated by users or devices and internet data. Google Trends data have been widely used in forecasting tourism arrivals and hotel occupancy to developed economies, such as demand for hotel rooms in Charleston, SC, or short-term tourist flows from South Korea to Japan {cite:p}`li2018big, li2021review`.

In the Pacific content during the Covid-19 pandemic, when timely data was not available, the International Monetary Fund (IMF) utilized Fiji’s official monthly tourism data, which had a latency of about 19 days and estimated visitor arrivals for other PICs. Their main assumption was that visitor arrivals from the same origin countries would have similar patterns for other PICs.

[^1]: <https://www.ifc.org/wps/wcm/connect/region__ext_content/ifc_external_corporate_site/east+asia+and+the+pacific/resources/solomon+islands+tourism+industry+guides+for+investors+and+government>
[^2]: See more in <https://www.statistics.gov.sb/statistics/visitor-arrivals#month>
