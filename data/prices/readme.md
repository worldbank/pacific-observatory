### PNG FPDA moving average price data July 2022
This is the original excel file with raw survey prices obtained from IFPRI https://www.ifpri.org/project/fresh-food-price-analysis-papua-new-guinea

###


In R code:

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
