
library(ggplot2)
library(naniar)
library(dplyr)
library(hrbrthemes, lib="C:/Users/wb514197/temp/R")
library(RColorBrewer)
library(zoo)
library(tidyr)

df <- read.csv("X:/data/pacific/output/adm1_climate_full.csv") %>%
  mutate(date = as.character(date)) 
  # select(-index, -month, -ADM1_PCODE, -ADM1_NAME, -ADM0_PCODE,
  #        -date, -year)

gg_miss_fct(x = df, fct = ADM0_NAME)

ggsave(paste0("../../docs/images/climate_coverage.jpeg"), width = 10, height = 6)


data <- df %>%
  group_by(ADM0_NAME, date) %>%
  summarise_if(is.numeric, mean, na.rm=TRUE) %>%
  mutate(
    date = as.Date(as.yearmon(date, format="%Y%m")),
    year = as.character(year),
  ) %>%
  mutate(
    month = format(date, "%b"),
    month_mm = format(date, "%m")
  ) %>%
  ungroup() %>%
  drop_na(c('spei12_mean'))


data <- df %>%
  filter(ADM0_NAME == "Vanuatu") %>%
  filter(ADM1_NAME == "Malampa") %>%
  mutate(
    date = as.Date(as.yearmon(date, format="%Y%m")),
    year = as.character(year),
  ) %>%
  mutate(
    month = format(date, "%b"),
    month_mm = format(date, "%m")
  ) %>%
  drop_na(c('spei03_mean'))

# arrange(month_mm, date=F) %>%

View(data[c('date', 'year', 'month', 'month_mm', 'spi03_mean')])

summary(data$spi03_mean)
# data[data$spi03_mean >2.5, "spi03_mean"]

ggplot(data) + 
  geom_raster(aes(month_mm, y = forcats::fct_rev(as.factor(year)), fill=spei12_mean)) +
  scale_fill_distiller(palette = "RdBu", limits=c(-2.5, 2.5), direction=1, oob = scales::squish) +
  theme_ipsum() +
  labs(y="", x="", fill="SPI 3") +
  facet_wrap(~ADM1_NAME)

# 3 month
ggplot(data) + 
  geom_col(aes(date, y = spi03_mean, fill=spi03_mean)) +
  scale_fill_distiller(palette = "RdBu", limits=c(-2.5, 2.5), direction=1, oob = scales::squish) +
  theme_ipsum() +
  labs(y="", x="") +
  facet_wrap(~ADM1_NAME)

# 12 month
ggplot(data) + 
  geom_col(aes(date, y = spei12_mean, fill=spei12_mean)) +
  scale_fill_distiller(palette = "RdBu", limits=c(-2.5, 2.5), direction=1, oob = scales::squish) +
  theme_ipsum() +
  labs(y="", x="") +
  facet_wrap(~ADM1_NAME)

# 12 month adm0
ggplot(data) + 
  geom_col(aes(date, y = spei12_mean, fill=spei12_mean)) +
  scale_fill_distiller(palette = "RdBu", limits=c(-2.5, 2.5), direction=1, oob = scales::squish) +
  theme_ipsum() +
  labs(y="", x="") +
  facet_wrap(~ADM0_NAME)


# ggplot(data) + 
#   geom_line(aes(as.integer(month_mm), y = spi03_mean, color=year)) +
#   # geom_smooth(aes(as.integer(month_mm), y = spi03_mean, color=year), se=FALSE) +
#   theme_ipsum() +
#   labs(y="", x="") +
#   facet_wrap(~ADM1_NAME)

# scale_fill_distiller(palette = "RdBu", limits=c(-2.5, 2.5), direction=1, oob = scales::squish) +
# coord_fixed(ratio=1)


