
library(dplyr)
library(ggplot2)
library(here)
# library(showtext)
library(scales)
library(lubridate)
library(hrbrthemes)

av_path <- 'C:/Users/wb514197/WBG/EEAPV Pacific Observatory Files - Geospatial and Big Data/Data/Aviation'
setwd(av_path)

df <- read.csv("rank_fl_data.csv", fileEncoding = 'UTF-8-BOM') %>%
  mutate(
    day = as.Date(Day.of.date, format="%B %d, %Y"),
    fl_wow_change = as.numeric(gsub("%", "", fl_wow_change)),
    fl_yoy_change  = as.numeric(gsub("%", "", fl_yoy_change))
    )

sel <- c("Fiji", "Palau", "Vanuatu", "Samoa")

# df <- df %>%
#   filter(destination_country=="Fiji")

df <- df %>%
  filter(destination_country %in% sel)

plt <- ggplot(df) +
  # geom_smooth(aes(x=day, y=flights_number_7days, color=destination_country, group=destination_country), 
  #             se=TRUE, span=1, linetype=0) +
  geom_point(aes(x=day, y=flights_number_7days, color=destination_country, group=destination_country),
             alpha=0.5, size=1.25) +
  facet_wrap(~destination_country, scales='free') +
  theme_minimal() +
  theme(legend.position="none") +
  labs(y="# of flights", x="", title="Number of flights per week")
plt




# ggplot(df) +
#   geom_line(aes(x=day, y=fl_wow_change, color=destination_country, group=destination_country)) +
#   theme_minimal()

df$week <- as.Date(cut(df$day, "week"))
df2 <- df %>%
  group_by(destination_country, week) %>%
  summarise_if(is.numeric, mean, na.rm = TRUE) %>%
  ungroup()
plt2 <- ggplot(df2) +
  # geom_smooth(aes(x=day, y=flights_number_7days, color=destination_country, group=destination_country), 
  #             se=TRUE, span=1, linetype=0) +
  geom_point(aes(x=week, y=flights_number_7days, color=destination_country, group=destination_country),
             alpha=0.5) + # size=1.25
  facet_wrap(~destination_country, scales='free') +
  theme_minimal() +
  theme(legend.position="none") +
  labs(y="# of flights", x="", title="Number of flights per week")
plt2

ggsave(paste0("./flights-per-week.jpeg"), width = 10, height = 6)


# df2 <- aggregate(flights_number_7days ~ Week, df, mean)

