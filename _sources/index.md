# Pacific Observatory

The Pacific Observatory is the World Bank analytical program to explore and develop new information sources to mitigate the impact of data gaps in official statistics for Papua New Guinea (PNG) and the Pacific Island Countries (PICs).

This repository hosts the team's efforts to investigate how alternative data sources can be used to generate economic and sector statistics through cost-effective methods. The goal is to assess whether new data sources can produce indicators that are timely, have higher frequency and granularity.

The content is structured by topic of investigation, each thematic folder contains code, notebooks, outputs, and feasibility notes.

## Research Topics

::::{grid} 1 2 3 3
:class-container: landing-grid
:gutter: 2

:::{grid-item-card}
:link: ./ais/ais_intro
:link-type: doc

Automatic Identification System (AIS)
^^^
This section assess the feasibility of using AIS data to derive high-frequency and geospatially disaggregated indicators on trade and fishing intensity.
:::

:::{grid-item-card}
:link: ./tourism/intro
:link-type: doc

Aviation Statistics
^^^
Monitor tourism recovery and fill gaps in visitors data through aviation statistics.
:::

:::{grid-item-card}
:link: ./text/intro
:link-type: doc

Text Analytics
^^^
Sentiment analysis and topic modeling from news sources to monitor economic uncertainty.
:::

:::{grid-item-card}
:link: ./access/access_intro
:link-type: doc

Market Access
^^^
Travel time analysis to study accessibility and connectivity in the Pacific.
:::

:::{grid-item-card}
:link: ntl/ch1_intro
:link-type: doc

Nighttime Lights Applications
^^^

- This note explores socio-economic applications with Night Time Lights data.
- Are lights at night a good proxy for economic activity or extractives?
- Can lights be used to aid poverty mapping, estimate access to electrification, or estimate damages/recovery from natural disasters?
:::

:::{grid-item-card}
Market Prices Imputation
^^^
- A machine learning imputation method to fill gaps in food prices from markets in Papua New Guinea, which follows the estimation from [here](https://openknowledge.worldbank.org/handle/10986/36778).
- The machine learning imputation code is available [here](https://github.com/worldbank/Food-Price-Estimation). 
:::

:::{grid-item-card}
:link: ./climate/climate_and_ag
:link-type: doc

Climate and Agriculture Monitoring
^^^

- Monitor crop productivity and seasonality through vegetation indices. 
- Develop a sub-national database of climate indicators.  
:::

:::{grid-item-card}
:link: ./poverty/vanuatu
:link-type: doc

Geospatial Poverty Map for Vanuatu
^^^
Small area estimation of poverty combining survey and geospatial data.
:::

:::{grid-item-card}
:link: https://ifeanyi-edochie.shinyapps.io/pciPTI/

Project Targeting Index
^^^
Dashboards with geo-spatial variables for project targeting.
:::
::::

## Additional Resources

🔖 [**Data Catalog Entry**](https://datacatalog.worldbank.org/search/dataset/0062856/Pacific-Observatory-Datasets)
> Catalog for output results.

🔖 [**High Frequency Phone Survey Dashboard**](https://dataviz.worldbank.org/views/Dashboard_v19/Income?%3Aembed=y&%3Aiid=1&%3AisGuestRedirectFromVizportal=y)
> Indicators from phone surveys.

## License

Materials under this repository are licensed under the [**World Bank Master Community License Agreement**](./LICENSE.md).