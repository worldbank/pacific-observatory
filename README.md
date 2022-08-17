# Pacific Observatory

The Pacific Observatory is the World Bank analytical program to explore and develop new information sources to mitigate the impact of data gaps in official statistics for Papua New Guinea (PNG) and the Pacific Island Countries (PICs).

This repository hosts the team's efforts to investigate how alternative data sources can be used to generate economic and sector statistics through cost-effective methods. The goal is to assess whether new data sources can produce indicators that are timely, have higher frequency and granularity.

The content is structured by topic of investigation, each thematic folder contains code, notebooks, outputs, and technical notes.

## Research Topics

🔖 **Night Time Lights Applications**
> This sections explores socio-economic applications with Night Time Lights data.  
Are lights at night a good proxy for economic activity?  
Can lights be used to aid poverty mapping, estimate access to electrification, or examine recovery from disasters or pandemic impacts?

🔖 **Market Prices Imputation**
> This section introduces a machine learning imputation method to fill gaps in food prices from markets in Papua New Guinea.


This follows the estimation proposed by

Andree, Bo Pieter Johannes. 2021. Estimating Food Price Inflation from Partial Surveys. Policy Research Working Paper;No. 9886. World Bank, Washington, DC. © World Bank. https://openknowledge.worldbank.org/handle/10986/36778 License: CC BY 3.0 IGO.

URI: http://hdl.handle.net/10986/36778 

The machine learning imputation code is avilable here https://github.com/worldbank/Food-Price-Estimation 

The code relies on WFP price surveys that are not available for PNG. The code has been adapted to run on IFPRI surveys available here https://www.ifpri.org/project/fresh-food-price-analysis-papua-new-guinea

This requires a few additional pre-processing steps to add coordinates and turn the IFPRI data into the required format. In R code:

```splus
library(data.table)
#' drop one or more columns from a data frame or matrix 
#'
#' @param x data frame or matrix with column names
#' @keywords data management
#' @export
#' @examples
#' x_minus_columns_a_and_b <- dropcol (x, c("a", "b"))
#' 
dropcol <- function(x, drop){
  x[,setdiff(colnames(x), drop )]
}


# markets coordinates
png_coordinates<-data.frame(
	lat = c(-5.8007167, -6.085636, -4.3521554, -6.0215373, -6.7137937, -5.2297248, -5.8568157, -9.4375208),
	lon = c(144.6230793, 145.38208, 152.2684985, 144.9641275, 146.9867278, 145.774455, 144.2291164, 147.1552402),
	row.names=c("Banz", "Goroka", "Kokopo", "Kundiawa", "Lae", "Madang", "Mt. Hagen", "Port Moresby"))


# replace this with an excel download call, or download the file from IFPRI and convert it to csv. 
# When this was last run, the PNG survey data could be ontained at 
# https://www.ifpri.org/project/fresh-food-price-analysis-papua-new-guinea
df <- data.frame(fread("PNG_july2022_prices.csv"))

missing_markets = setdiff(unique(df$market), rownames(png_coordinates))
if(length(missing_markets)){
  print(paste("MARKETS ARE MISSING IN COORDINATES TABLE:", missing_markets))
}

df$lat <- df$lon <- NA

for(mkt in rownames(png_coordinates)){
	df[df$market==mkt, c("lat", "lon")] <- matrix( as.numeric(png_coordinates[rownames(png_coordinates)==mkt,]), ncol=2, nrow=nrow(df[df$market==mkt, c("lat", "lon")]), byrow=TRUE)
}

# some formatting
drops = c("date", "day","average_month_range", "movingave_a", "movingave_b", "movingave_c", "movingave_d", "movingave_e", "movingave_f")
  df=dropcol(df, c(drops, paste0(drops,".")) )
  df$adm1_name  <- df$adm2_name <- df$market
  colnames(df)[colnames(df)=="market"]<-"mkt_name"
  df$category <- "vegetables and fruits"
  df$um_name <- "unit"
  df$cur_name <- "PGK"
  df$country <- df$adm0_name <- "Papua New Guinea"
  df$ISO3 <- "PNG"
  colnames(df)[colnames(df)=="unitprice"]<-"price"
  colnames(df)[colnames(df)=="crop"]<-"cm_name"
  df$priceflag <- "actual"

fwrite(df, "PNG_july2022_prices_wc.csv")

```

After preparing the raw data, the following section in the ```main.R``` file of the price imputation code should be changed to read the data:

### Original code
```splus
  if("Papua New Guinea" %in% selected_country_list){
    cat("adding PNG from file")
    PNG <- read.csv("PNG_dec_prices_wc.csv")
    PNG$time_id <- NA 
      rawMarketPrices = rbind(rawMarketPrices, PNG[PNG$year>=data_startyear,])
      rawMarketPrices$time_id <- generate_T(rawMarketPrices$year, rawMarketPrices$month)
  }
```
### New code
```splus
  if("Papua New Guinea" %in% selected_country_list){
    cat("adding PNG from file")
    PNG <- read.csv("PNG_july2022_prices_wc.csv") ##### <---------- Change the name of the file. 
    PNG$time_id <- NA 
      rawMarketPrices = rbind(rawMarketPrices, PNG[PNG$year>=data_startyear,])
      rawMarketPrices$time_id <- generate_T(rawMarketPrices$year, rawMarketPrices$month)
  }
```
Also make sure that ```splus selected_country_list = "Papua New Guinea"```

🔖 **Automatic Identification System (AIS)**
> This section assess the feasibility of using AIS data to derive high-frequency and geospatially disaggregated indicators on fisheries and trade.

🔖 **Crop Mapping**
> Creating new crop masks with limited training data and satellite imagery.  
> Developing a sub-national database of climate indicators.

🔖 **Aviation Statistics**
> Developing a sub-national database of climate indicators.

## Additional Resources

- [DIME Analytics Data Handbook](https://worldbank.github.io/dime-data-handbook/)
    > This book is intended to serve as an introduction to the primary tasks required in development research, from experimental design to data collection to data analysis to publication. It serves as a companion to the DIME Wiki and is produced by DIME Analytics.

- [GitHub Pages](https://guides.github.com/features/pages/)
    > GitHub Pages are public webpages hosted and easily published through GitHub.

- [Jupyter Book](https://jupyterbook.org/intro.html)
    > Jupyter Book is an open source project for building beautiful, publication-quality books and documents from computational material.

## License

Materials under this repository are open-source under an [MIT license](LICENSE). The community is invited to test, adapt, and re-purpose materials as needed.
