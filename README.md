# Pacific Observatory

The Pacific Observatory is the World Bank analytical program to explore and develop new information sources to mitigate the impact of data gaps in official statistics for Papua New Guinea (PNG) and the Pacific Island Countries (PICs).

This repository hosts the team's efforts to investigate how alternative data sources can be used to generate economic and sector statistics through cost-effective methods. The goal is to assess whether new data sources can produce indicators that are timely, have higher frequency and granularity.

The content is structured by topic of investigation, each thematic folder contains code, notebooks, outputs, and feasibility notes.

![Logo](https://github.com/worldbank/pacific-observatory/blob/main/docs/images/logo.png)

## Research Topics

🔖 **Night Time Lights Applications**
> This note explores socio-economic applications with Night Time Lights data.  
> Are lights at night a good proxy for economic activity or extractives?  
> Can lights be used to aid poverty mapping, estimate access to electrification, or estimate damages/recovery from natural disasters?

🔖 **Market Prices Imputation**
> A machine learning imputation method to fill gaps in food prices from markets in Papua New Guinea.


This follows the estimation proposed by

> [Andree, Bo Pieter Johannes. 2021. Estimating Food Price Inflation from Partial Surveys. Policy Research Working Paper;No. 9886. World Bank, Washington, DC. © World Bank.](https://openknowledge.worldbank.org/handle/10986/36778) License: CC BY 3.0 IGO.
> 
> [URI](http://hdl.handle.net/10986/36778)

To improve the results for Papua New Guinea, a two-stage nonlinear estimation procedure for low-data regimes was suggested by

> Andree, Bo Pieter Johannes; Pape, Utz Johann. 2023 (Forthcoming). Can co-deployment of machine learning and high-frequency surveys produce reliable real-time data in data-scarce regions?. Policy Research Working Paper. World Bank, Washington, DC. 

Andree and Pape (2023) also suggest using the institutional exchange rate as a trend variable and narrow down the tuning grid of the cubist algorithm to improve processing speeds when handling a large number of price items.

The machine learning imputation code is available [here](https://github.com/worldbank/Food-Price-Estimation)

The code relies on WFP price surveys that are not available for PNG. The code has been adapted to run on IFPRI surveys available [here](https://www.ifpri.org/project/fresh-food-price-analysis-papua-new-guinea)

This requires a few additional pre-processing steps to add coordinates and turn the IFPRI data into the required format. See pacific-observatory/data/prices/

After preparing the raw data, the following section in the ```main.R``` file of the price imputation code should be changed to read the data:

### Original code
```splus
  if("Papua New Guinea" %in% selected_country_list){
    cat("adding PNG from file")
    PNG <- read.csv("PNG_dec_prices_wc.csv") ##### <---------- Original PNG price data file name. 
    PNG$time_id <- NA 
      PNG=dropcol(PNG, setdiff(colnames(PNG), colnames(rawMarketPrices)))
      rawMarketPrices = rbind(rawMarketPrices, PNG[PNG$year>=data_startyear,])
      rawMarketPrices$time_id <- generate_T(rawMarketPrices$year, rawMarketPrices$month)
    # historical mode
    historical_mode =TRUE
    if(historical_mode){
      rawMarketPrices=rawMarketPrices[rawMarketPrices$time_id<=max(rawMarketPrices$time_id[rawMarketPrices$adm0_name=="Papua New Guinea"]), ]
        unique(rawMarketPrices$time_id) -> time_id
    }
  }
}
```
### New code
```splus
  if("Papua New Guinea" %in% selected_country_list){
    cat("adding PNG from file")
    PNG <- read.csv("PNG_july2022_prices_wc.csv") ##### <---------- Point the code to the new file name. 
    PNG$time_id <- NA 
      PNG=dropcol(PNG, setdiff(colnames(PNG), colnames(rawMarketPrices)))
      rawMarketPrices = rbind(rawMarketPrices, PNG[PNG$year>=data_startyear,])
      rawMarketPrices$time_id <- generate_T(rawMarketPrices$year, rawMarketPrices$month)
    # historical mode
    historical_mode =TRUE
    if(historical_mode){
      rawMarketPrices=rawMarketPrices[rawMarketPrices$time_id<=max(rawMarketPrices$time_id[rawMarketPrices$adm0_name=="Papua New Guinea"]), ]
        unique(rawMarketPrices$time_id) -> time_id
    }
  }
```
Also make sure that Papua New Guinea is included in the country list:
```splus
selected_country_list = c("Afghanistan", "Papua New Guinea") 
```
To produce results for different time periods, change
```splus
data_startyear = 2009
```
🔖 **Aviation Statistics**
> Monitor tourism recovery through aviation statistics.

🔖 **Climate and Agriculture Monitoring**
> Monitor crop productivity and seasonality through vegetation indices.  
> Develop a sub-national database of climate indicators.  
> Update crop masks with limited training data and satellite imagery. 

### Future work

🔖 **Automatic Identification System (AIS)**
> This section assess the feasibility of using AIS data to derive high-frequency and geospatially disaggregated indicators on trade and fishing intensity.

🔖 **Text Mining**
> Study social dynamics (conflict risk, cohesion, perceptions of the economy, climate change) through mining from text sources (ACLED, GDELT). 

## Additional Resources

- [DIME Analytics Data Handbook](https://worldbank.github.io/dime-data-handbook/)
    > This book is intended to serve as an introduction to the primary tasks required in development research, from experimental design to data collection to data analysis to publication. It serves as a companion to the DIME Wiki and is produced by DIME Analytics.

- [GitHub Pages](https://guides.github.com/features/pages/)
    > GitHub Pages are public webpages hosted and easily published through GitHub.

- [Jupyter Book](https://jupyterbook.org/intro.html)
    > Jupyter Book is an open source project for building beautiful, publication-quality books and documents from computational material.

## License

Materials under this repository are open-source under an [MIT license](LICENSE). The community is invited to test, adapt, and re-purpose materials as needed.
