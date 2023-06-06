# Introduction

Tourism has been a significant component of the Pacific Islands Countries (PICs) economy, driving economic growth. However, limited access to essential data and information obstructs sustainable development. For example, in the Solomon Islands, an International Finance Corporation (IFC) report estimated that tourism contributes to 10.5\% of the Gross Domestic Product (GDP) and 10.8\% of employment. [^1] Meanwhile, the latest available tourist data is from the fourth quarter of 2020, and a two-year data vacuum exists. [^2] The lagged data is not unique to the Solomon Islands, but more of a general situation for PICs.

What is worse, when Covid-19 hit globally, tourism came to a pause for PICs. Recovery slowly takes place, and data plays a more significant role in understanding how long PICs could bounce back. By leveraging alternative data sources, such as flight data, and combining them with the available historical data, we can better understand the Pacific Islands countries' economic and social conditions.

The report will be divided into five parts \[temporarily\]. The first part reviews the literature about tourism and development, specifically focusing on PICs, and the main forecasting models employed in tourism research. Then, the second part introduces the sources and features of the official and flight data and assesses their relevance by correlational and time series analysis. The third part describes the empirical modeling strategies and robustness checks. The fourth part will display the results from the model.

## Literature Review

### Tourism and Growth 

Tourism has been recognized as a key driver of economic growth in developing countries. As {cite:t}`brida2016has` reviewed approximately 100 journal articles on tourism, tourism-led growth hypothesis has been supported by most studied countries with a few exceptions. {cite:t}`seetanah2011assessing` examines 19 island economies, reveals a bi-causal relationship between tourist and growth, and confirms the fact that "tourism development on island economies may have comparatively higher growth effects."

{cite:t}`narayan2013does` found that a 1% increase in tourism exports leads to a 0.72% long-term increase in GDP and a 0.24% short-term increase in Pacific Islands countries. {cite:t}`kumar2021tourism` focused specifically on Fiji, Samoa, Solomon Islands, Tonga, and Vanuatu and found that tourism development is growth-enhancing for all five countries. An earlier article by {cite:t}`narayan2004fiji` found that “growth in income in Fiji’s main tourist source markets [New Zealand, Austria, and US] has a positive impact on visitor arrivals.” These studies collectively provide compelling evidence of the significant contribution of tourism to economic growth and development in PICs.

### Forecast

Tourism forecasting has been fundamental to tourism research and management, and various approaches have been used to generate the forecasts. As {cite:t}`song2019review` suggest, most tourism forecasts fall into four categories: *time series*, *econometric*, *AI-based*, and *judgmental* models. Time series models forecast based in historical patterns, econometric models focus on causes and effects of economic factors to tourism, and AI-based models take advantage of the recent advancements in deep neural networks.  

Beyond individual forecasts, there has been a trend to combine individual forecasts to improve accuracy. As {cite:t}`timmermann2006forecast` reviews, forecast combinations have, on average, outperformed the single best forecasts, with the evidence from [M-3 Competition](https://forecasters.org/resources/time-series-data/m3-competition/) and {cite:t}`stock1998comparison`. The explanations behind the superiority of combination are mainly from “incorporat\[ing\] partial (but incompletely overlapping) information” and mitigating the structural breaks and instabilities with varying degrees of misspecification and adaptability {cite:p}`wang2022forecast`.

In terms of the combination schemes, they can be linear or non-linear, static or time-varying, series-specific or cross-learning, and consider or ignore correlations among individual forecasts {cite:p}`wang2022forecast`. The most straightforward one is the equally weighted average method, which can be easily implemented by calculating the simple arithmetic average of forecasts. Despite ignoring the precision of individual forecasts and correlations between errors, the method often works well compared to complex combination schemes, the phenomenon called “forecasting combination puzzle.”

The linear combination scheme is built on the idea that greater weights should be assigned to the most accurate forecast method. The exemplary one is relative performance weights, which are based on each model’s relative MSE performance. Least-square estimator of the weights was introduced by {cite:ts}`granger1984improved`. In the seminal work, teprohey recommended that weights can be estimated by the ordinary least squares (OLS) with past observations as the response variable and individual forecasts as the predictor variables. Researchers also relate the combination estimation to the shrinkage methods, aiming to strike a balance between information and noise/bias from individual forecasts or solving the estimation uncertainty under, such as LASSO- and Ridge- procedures {cite:p}`diebold2019machine`.

Despite that forecast combinations captured numerous attentions from 1980s, only 17 of a pool of 211 tourism studies involve the forecast combination, and most of them were conducted in late 2000s, like {cite:p}`wong2007tourism`.

### Tourism Data

Although tourist arrivals remain pivotal in tourism forecasting, recent studies have taken advantage of big data by users or devices and internet data {cite:p}`li2018big, li2021review`. Google Trends data have been widely used in forecasting tourism arrivals and hotel occupancy to developed economies, such as demand for hotel rooms in Charleston, SC or short-term tourist flows from South Korea to Japan {cite:p}`pan2012forecasting, park2017short`.  

In the context of PICs during the Covid-19 pandemic when timely data was not available, the International Monetary Fund (IMF) utilizes Fiji’s official monthly tourism data, which had a quick turnaround of about 19 days, and produces the estimates of visitor arrivals for other PICs, helping monitor the tourism industry. The hidden assumption is that visitor arrivals by the departure countries could have similar patterns for PICs.

[^1]: <https://www.ifc.org/wps/wcm/connect/region__ext_content/ifc_external_corporate_site/east+asia+and+the+pacific/resources/solomon+islands+tourism+industry+guides+for+investors+and+government>
[^2]: See more in <https://www.statistics.gov.sb/statistics/visitor-arrivals#month>
