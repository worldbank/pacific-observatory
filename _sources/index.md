# Pacific Observatory

The Pacific Observatory is the World Bank analytical program to explore and develop new information sources to mitigate the impact of data gaps in official statistics for Papua New Guinea (PNG) and the Pacific Island Countries (PICs).

This repository hosts the team's efforts to investigate how alternative data sources can be used to generate economic and sector statistics through cost-effective methods. The goal is to assess whether new data sources can produce indicators that are timely, have higher frequency and granularity.

The content is structured by topic of investigation, each thematic folder contains code, notebooks, outputs, and feasibility notes.

## Research Topics

::::{grid} 1 2 3 3
:class-container: landing-grid
:gutter: 2

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
- The code relies on WFP price surveys that are not available for PNG. The code has been adapted to run on IFPRI surveys available [here](https://www.ifpri.org/project/fresh-food-price-analysis-papua-new-guinea)
:::

:::{grid-item-card}
:link: ./tourism/intro
:link-type: doc

Aviation Statistics
^^^
Monitor tourism recovery through aviation statistics.
:::

:::{grid-item-card}
:link: ./climate/climate_and_ag
:link-type: doc

Climate and Agriculture Monitoring
^^^

- Monitor crop productivity and seasonality through vegetation indices. 
- Develop a sub-national database of climate indicators.  
- Update crop masks with limited training data and satellite imagery.
:::

:::{grid-item-card}
:link: ./poverty/vanuatu
:link-type: doc

Geospatial Poverty Map for Vanuatu
^^^
Small area estimation of poverty combining survey and geospatial data.
:::

:::{grid-item-card}
:link: ais_intro
:link-type: doc

Automatic Identification System (AIS)
^^^
This section assess the feasibility of using AIS data to derive high-frequency and geospatially disaggregated indicators on trade and fishing intensity.
:::
::::

<!-- 🔖 [**Night Time Lights Applications**](./ntl/ch1_intro.md)
> This note explores socio-economic applications with Night Time Lights data.  
> Are lights at night a good proxy for economic activity or extractives?  
> Can lights be used to aid poverty mapping, estimate access to electrification, or estimate damages/recovery from natural disasters?

🔖 **Market Prices Imputation**
> A machine learning imputation method to fill gaps in food prices from markets in Papua New Guinea.

This follows the estimation proposed by

[Andree, Bo Pieter Johannes. 2021. Estimating Food Price Inflation from Partial Surveys. Policy Research Working Paper;No. 9886. World Bank, Washington, DC. © World Bank.](https://openknowledge.worldbank.org/handle/10986/36778) License: CC BY 3.0 IGO.

[URI](http://hdl.handle.net/10986/36778)

The machine learning imputation code is available [here](https://github.com/worldbank/Food-Price-Estimation)

The code relies on WFP price surveys that are not available for PNG. The code has been adapted to run on IFPRI surveys available [here](https://www.ifpri.org/project/fresh-food-price-analysis-papua-new-guinea)

🔖 [**Aviation Statistics**](./tourism/intro)
> Monitor tourism recovery through aviation statistics.

🔖 [**Climate and Agriculture Monitoring**](./climate/climate_and_ag.md)
> Monitor crop productivity and seasonality through vegetation indices.  
> Develop a sub-national database of climate indicators.  
> Update crop masks with limited training data and satellite imagery.  

🔖 [**Automatic Identification System (AIS)**](./ais_intro.md)
> This section assess the feasibility of using AIS data to derive high-frequency and geospatially disaggregated indicators on trade and fishing intensity.

🔖 [**Geospatial Poverty Maps**](./poverty/vanuatu)
> Small area estimation of poverty combining survey and geospatial data.

🔖 [**Project Targeting Index**](https://ifeanyi-edochie.shinyapps.io/pciPTI/)
> Geospatial variables for project targeting. -->

## Additional Resources

::::{grid} 1 2 3 3
:class-container: landing-grid
:gutter: 2

:::{grid-item-card}
:link: https://guides.github.com/features/pages/

GitHub Pages
^^^
GitHub Pages are public webpages hosted and easily published through GitHub.
:::

:::{grid-item-card}
:link: https://jupyterbook.org/intro.html

Jupyter Book
^^^
Jupyter Book is an open source project for building beautiful, publication-quality books and documents from computational material.
:::


:::{grid-item-card}
:link: https://github.com/worldbank/template

🚀 World Bank Template
^^^
Standardized, but flexible project and documentation structure of folders and files for sharing your data science work maintained by the World Bank Development Data Group.
:::
::::

## License

Materials under this repository are licensed under the [**World Bank Master Community License Agreement**](../LICENSE.md).