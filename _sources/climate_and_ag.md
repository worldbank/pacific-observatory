# Climate and Agriculture Monitoring in the Pacific Island Countries

Agriculture is an essential activity for the majority of Papua New Guineans. About 80% of the food consumed in PNG is produced within the nation, and the largest component of agriculture is subsistence farming. Despite its importance for rural livelihoods, there is a dearth of recent data on agriculture in the public domain.  

The populations in the Pacific Island Countries (PIC) are at disproportionately higher risk of adverse consequences from global warming. Current impacts include increasing droughts and water scarcity, coastal flooding and erosion, and changes in rainfall that affect food production (IPCC 2018). Weather conditions and climate variations have profound impacts on agriculture, water resources and on the socioeconomic opportunities and adaptations of the region.  

Optical images and climate variables captured by satellites can be a powerful source of information to address data gaps and inform climate assessments. There is a wealth of underutilized satellite data that can be useful to monitor climate events, agricultural productivity, and provide insights for better preparedness and mitigation strategies. Historical and real-time indicators can be a critical input to short and long-term planning, operational decision making, adaptive infrastructure development and the management of climate risks.  

The objective of this note is to showcase examples of how public satellite data can inform our understanding of climate risks and agricultural activity in the Pacific region. The examples developed use low-to-medium resolution Earth Observation (EO) data to monitor changes in hydro-meteorological conditions and detect growing seasons. The climate data was collated for the Pacific Observatory and is being made available in tabular and raster formats through the Development Data Catalog.  

The note is divided into 5 sections. Sections 1 through 3 showcase various climate datasets, including rainfall anomalies and drought indices, and describe use cases where these signals can provide critical insights. Section 4 explores how agricultural seasonality parameters can be derived from Vegetation Indices (VIs) produced with optical imagery. The last section introduces resources to find data for climate projections.

## Climate Variability

Climate variability directly influences many dimensions of food security, particularly food access and availability. Variation in rainfall is a common element of many natural disasters – droughts, floods, typhoons, and tsunamis – and is influenced by global, regional, and local factors. Global climate factors include El Niño-Southern Oscillation (ENSO); regional factors include the Madden-Julian Oscillation, West Pacific Gradient (WPG) and fluctuations in the sea surface temperature (SST) of the Pacific Ocean; and local factors include elevation, island position, the circulation of land and sea breezes, and land cover.  

The level of climate risk can be measured based on the strength of ENSO signal on rainfall variability using correlation analysis. Loss of food production in Southeast Asia and the Pacific is closely associated with the ENSO phenomena (Naylor et al, [2001](https://doi.org/10.1023/A:1010662115348), [2007](http://dx.doi.org/10.1073/pnas.0701825104)). Anderson specifically indicates ENSO poses risks to crop production in the greater Pacific Basin region [2018](https://doi.org/10.1016/j.agrformet.2018.07.023). El Nino years are normally associated with drought years, while La-Niña is often related to wet years which can cause flood hazards. The correlation analysis is applied to monthly rainfall anomaly and sea surface temperature anomaly in the four NINO regions along the equator:  

* Niño 1 (80°-90°W and 5°-10°S)
* Niño 2 (80°-90°W and 0°-5°S)
* Niño 3 (90°-150°W and 5°N-5°S)
* Niño 4 (150°-160°E and 5°N-5°S)

![nino](./images/climag/climag-ninoregion.jpeg)

**Figure 1.** NINO regions. Source: https://www.weather.gov/jetstream/enso

The NINO region is optimal for monitoring ENSO and its impacts, while the WPG is measured as the difference in SST between the NINO4 region and the West Pacific region. When the West Pacific is warm during La Niña events, the changes across the globe can be extreme.  

Simple regression analysis is applied to examine the correlation between rainfall anomaly in each area to anomaly of sea surface temperature in the Pacific Ocean which represent ENSO signals.

`Y = aX + b`, where: `Y` = Rainfall anomaly, `b` = `Y` intercept, `a` = Slope and `X` = SST anomaly

![nino34](./images/climag/climag-pci-precip-sst.png)

**Figure 2.** General sensitivity of rainfall to SST changes in NINO3.4 region

The map in Figure 2 demonstrates the change in monthly rainfall associated with a one degree decrease in SST in NINO-3.4 region. Red highlighted areas on the map such as Tuvalu, Kiribati, Nauru, and partly New Britain and Bougainville Island of PNG would be severely affected or experience 10 to 50 mm below normal rainfall by 1°C change in SST. In contrast, dark blue highlighted areas would experience at least 50mm more of rainfall in the respective month.  

ENSO signals used to be the key indicators for agriculture production in some areas. However, negative impacts of the signals to food production have been mitigated with a wide range of adaptations like improvement of irrigation facilities, and innovations of drought and flood tolerant crop varieties. Still, the signals remain helpful for hydro-meteorological disasters forecast.  

## Climate Monitoring

This section introduces satellite-derived climate datasets that can be monitored with different temporal resolutions (monthly, daily, and forecast). The variables covered include precipitation, temperature, evapotranspiration, and drought indices. Monitoring these variables in a real-time fashion allows for early detection of water stress in vegetation and helps us prepare for different types of climate impacts.  

### Monthly and Seasonal

The Standardized Precipitation-Evapotranspiration Index (SPEI) is an established indicator to detect, monitor, and analyze droughts. The SPEI considers how various climate variables (precipitation, evapotranspiration, temperature) relate to normal conditions and can be calculated according to different temporal scales. The multi-scalar character of this indicator makes it a suitable proxy to identify dry and wet conditions related to soil moisture, which can have significant impacts on agriculture.  

![spei-wet](./images/climag/climag-png-spei-wet.png)

**Figure 3.** Wet condition

Figures 3 and 4 indicate the percentage of districts that experience a certain level of SPEI (dryness or wetness) by month. In December 2020, close to 70% of districts in Papua New Guinea experienced wet conditions, 20% were exceptionally wet, and only about 10% experienced normal conditions. PNG has been relatively wet in the last 20 years, although the ENSO signal drove a significant dry period during 2015-2016.  

![spei-dry](./images/climag/climag-png-spei-dry.png)

**Figure 4.** Dry condition

Showing the inverse of Figure 3, Figure 4 indicates months with dryer than usual climate for example during the strong El Nino of 2015-2016. Monthly SPEI data can provide valuable lead time to identify the slow onset of cumulative climate impacts. From the data, we can discern how the dry or wet situation is evolving month-by-month, year-by-year.  

The maps below show the spatial disaggregation in the SPEI data, highlighting the contrast from two time periods with drastically different trends: December 2015 (Strong El Nino) and December 2020 (Moderate La Nina).  

![spei-wet](./images/climag/climag-png-spei-maps.png)

**Figure 5.** SPEI 12-months

Long-term historical information is key to understand what happened in the past and identify climate variability across regions. 60-years of SPEI data is a valuable resource to study the main impacts of increased temperatures on water demand.  

### Daily

Daily estimates of extreme rainfall are available based on satellite microwave precipitation estimates. The following section demonstrates how daily weather data can be utilized to inform early warning systems and disaster response policies.  

![extreme-rain](./images/climag/climag-png-extreme-rain.png)

**Figure 6.** Extreme rainfall

Daily rainfall data can inform policy through various mechanisms:  
1.	Input to early warning systems and trigger anticipatory actions.
2.	Will it cause a landslide?
3.	Which roads will be affected? 
4.	How many populations and cropland will be affected? 
5.	Which area is in early planting and will be damaged?  

Another multi-temporal indicator of meteorological conditions is maximum consecutive dry days (CDD). This index captures the cumulative effect of consecutive days without precipitation (days with less than 1 mm of rain). CDD can be updated on daily basis and serve as an effective measure of seasonal droughts. 

![max-cdd](./images/climag/climag-fiji-max-cdd.png)

**Figure 7.** Maximum consecutive dry days in 2021

### Forecast

Sub-seasonal and seasonal forecasts of precipitation and temperature are available via the [International Research Institute (IRI) of Columbia University](http://iridl.ldeo.columbia.edu/maproom/Global/ForecastsS2S/index.html). The forecasts provide relevant information for key events, such as the timing of the onset of the rainy season, important for agriculture, or the risk of extreme rainfall events or heat waves, critical for public safety. In Figure 8, shades of brown indicate a forecast of drier conditions, whereas shades of blue indicate a forecast of wetter conditions.  

#### 1.	Sub-seasonal Forecast: Optimum planting and harvest potential

Sub-seasonal forecasts predict key variables (temperature or precipitation) on a weekly basis up to one month ahead. Historical records of planting in combination with these forecasts are helpful to draw a recommendation on optimal planting dates. Weather forecasts released during the 2nd or 3rd planting season enable actors to plan for optimum yield, meaning that they can identify which type of crops will grow best given the forecasted precipitation level. Similarly, the forecasts can identify which areas can grow secondary crops and inform decisions over how to distribute seeds.  

![subx-precip](./images/climag/climag-subx-precip.png)

**Figure 8.** Sub-seasonal Forecast Precipitation. Source: IRI

![subx-temp](./images/climag/climag-subx-temp.png)

**Figure 9.** Sub-seasonal Forecast Temperature. Source: IRI

#### 2.	Seasonal Forecast: Opportunities during climate extreme events

Seasonal forecasts provide longer time-intervals and are usually available up to 7 months in advance. Sub-seasonal forecasts are more accurate than seasonal forecasts as they predict less far into the future. Seasonal forecasts are necessary for optimizing harvest in the long-term. If a planted area is damaged by a flood or drought event, replantation programs can be designed considering long-term forecasts. Replantation programs can be initiated if long-term rainfall forecasts are favorable.  

![seasonal-precip](./images/climag/climag-seasonal-precip.png)

**Figure 10.** Seasonal Forecast Precipitation. Source: IRI
	
![seasonal-temp](./images/climag/climag-seasonal-temp.png)

**Figure 11.** Seasonal Forecast Temperature. Source: IRI

## Cyclone Season

Cyclone patterns are important to track in the Pacific as they can indicate which areas are more vulnerable and likely to suffer loss of agricultural production due to extreme rainfall. Traditionally, areas of tropical cyclone formation are divided into seven basins.  

![tc-regions](./images/climag/climag-tc-regions.png)

**Figure 12.** Tropical cyclone centers and regions. Source: https://en.wikipedia.org/wiki/File:Tropical_Cyclone_Centers_and_Regions.png 

1. Western Pacific Ocean

The West Pacific Ocean is the most active basin on the planet, accounting for one-third of all tropical cyclone activity. Annually, an average of 25.7 cyclones in the basin acquire tropical storm strength, and an average of 16 typhoons per year were recorded during 1968 to 1989. The basin sees activity year-round, but cyclone activity is at its minimum in February/March.  

![tc-north](./images/climag/climag-pci-tc-north.jpeg)

**Figure 13.** Tracks of all tropical cyclones in the northwestern Pacific Ocean between 1980 and 2005. The vertical line to the right is the International Date Line. Source: https://en.wikipedia.org/wiki/Tropical_cyclone_basins

2. South Pacific Ocean

Tropical Cyclones that develop within the South Pacific basin generally affect countries to the west of the international dateline, though during years of the warm phase of ENSO cyclones have been known to develop to the east near French Polynesia. On average, the basin sees nine tropical cyclones annually with about half of them becoming severe tropical cyclones.  

![tc-south](./images/climag/climag-pci-tc-south.jpeg)

**Figure 14.** Tracks of all tropical cyclones in the southwestern Pacific Ocean between 1980 and 2005. Source: https://en.wikipedia.org/wiki/Tropical_cyclone_basins

Figure 15 shows that during December to May cyclone events occur mostly in the South Pacific Ocean, whereas from June to December most cyclone events happen in West Pacific Ocean.  

![tc-2019](./images/climag/climag-tc-2019.png)

**Figure 15.** Tropical cyclone happen in 2019. Source: https://upload.wikimedia.org/wikipedia/en/timeline/4dea2f730b024e57a1db72e8dc62f515.png 

## Agriculture Monitoring

Climate and vegetation data sourced from remote sensing satellites are widely used for agricultural monitoring, especially in the growing season. Agricultural monitoring with remote sensing is often conducted with medium-low resolution imagery because public satellites provide long-term coverage and stable revisit rates. These data provide useful information for:  

* Providing early warning before climate shocks threaten food security.
* Contextual analysis needed to plan interventions. For example, market operations when crop scarcity occurs.
* Availability of cropland area for spring crop planting possibly damaged during conflict or emergency situations.  

Whether food is produced by households or bought from local markets, for domestic consumption or commercial purpose, earth observation can be a useful tool to provide information on the status of cultivation and harvested areas.  

### Remote sensing data requirements for vegetation monitoring

#### A) Operational data production
Data needs to be available on a routinely basis, ideally with a set time interval.  

#### B) Definition of historical conditions
Historical averages are useful to then calculate anomalies, deviations from normal conditions, percentage change, or ranking maps. This is critical to provide context of how current conditions compare to the historical conditions for a specific location and time during the year. They also enable the differentiation of moderate, severe, and extreme drought events.  

### Vegetation Indices

The Enhanced Vegetation Index (EVI) is an ‘optimized’ index designed to enhance the vegetation signal with improved sensitivity in high biomass regions and improved vegetation monitoring through a de-coupling of the canopy background signal and a reduction in atmosphere influences.  

![EVI](./images/climag/climag-evi-2021.png)

**Figure 16.** MODIS EVI, 2021

While the Normalized Difference Vegetation Index (NDVI) is chlorophyll sensitive, the EVI is more responsive to canopy structural variations, including leaf area index (LAI), canopy type, plant physiognomy, and canopy architecture.  

![NDVI](./images/climag/climag-ndvi-2021.png)

**Figure 17.** MODIS NDVI, 2021

### Methodology

A working example has been developed based on areas where the majority of cropland is paddy. This approach requires a crop type mask and moderate resolution time series Vegetation Indices (VI). This example uses data from the MODIS Terra Vegetation Indices (MOD13Q1), available at 250m spatial resolution and 16-days of temporal resolution.  

![TIMESAT-gs](./images/climag/climag-growing-season.png)

**Figure 18.** Growing season

State of planting and harvesting estimates are determined by importing Vegetation Indices (VI) data into [TIMESAT](http://web.nateko.lu.se/timesat/timesat.asp) – a program for analyzing time-series satellite sensor data. TIMESAT conducts pixel-by-pixel classification of satellite images to determine whether planting has started or not. This process is followed for all areas over multiple years to evaluate current planting vis-à-vis historical values from 2003 - 2021 (in this case with MODIS VI).

![TIMESAT](./images/climag/climag-timesat-parameters.png)

**Figure 19.** TIMESAT Parameters

The main seasonality parameters generated in TIMESAT are (a) beginning of season, (b) end of season, (c) length of season, (d) base value, (e) time of middle of season, (f) maximum value, (g) amplitude, (h) small integrated value, (h+i) large integrated value. The blue line in Figure 19 is the real EVI value and red is EVI value after applying a Savitsky-Golay smoothing algorithm. Phenological events are sensitive to climate variation. Therefore, phenology data provide important baseline information for assessment of ecological trends and detection of climate change impacts on multiple scales.  

These phenological parameters are related to the seasonal vegetation productivity by considering both agricultural production and available biomass. Comparing current VI values with the long-term average, and with the minimum and maximum values, helps to better understand the performance of the vegetative season and its expected productivity.

### Growing Season

Information on the onset of planting seasons (and harvest time) are relevant for decision makers like to see.  

![TIMESAT-sos](./images/climag/climag-timesat-sos.png)

**Figure 20.** Beginning of Season.

The map in Figure 20 shows the start of the season, or planting date, for crop areas across Kavieng District. This map provides a starting point for future monitoring of the crop planting status.  

1.	How many districts are behind in planting? If there is a delay in some districts, is planting acceleration necessary?
2.	How many hectares are available for next planting?
3.	Is the current harvest enough for domestic consumption?

Decision makers also need this kind of seasonal monitoring and data triangulation and information to decide:  

1.	Planting potential for the next 3-months: assigning the distribution of agricultural inputs.
2.	Mobilization of extension workers to monitor and implement mitigation strategies: adjustment of irrigation system in anticipation of drought or flood, pest control of infestation/disease to avoid crop failure, reservoir readiness for planting season.
3.	Preparation of policy recommendations: assess ongoing situation, harvest estimate, price protection.  

This information is necessary for both policy makers, farmers, and other agricultural actors (cooperatives, rural businesses). Negative consequences can be anticipated months ahead and resources can be prioritized on areas with greater potential.  

### Limitations and Assumptions

Getting high-quality VI data for all timesteps is challenging due to frequent interruptions caused by clouds. Other data quality issues with optical imagery include snow/ice, aerosol quantity, shadows). Due to these factors, the general quality of MODIS or Sentinel-2 data varies per year, affecting the comparisons of VIs and estimated cultivated area.  

![cloud-ts](./images/climag/cloud-ts.png)

**Figure 21.** Sentinel-2 data quality for a selected crop area in the Eastern Highlands, PNG

Vegetation Indices based on Synthetic Aperture Radar (SAR) are a good alternative and should be explored further for the Pacific context.  

This analysis was based on publicly available MODIS data and a global cropland extent map from the Global Food Security-Support Analysis Data (GFSAD). Because this map only provides a binary indication of where crops are, the seasonal parameters presented are for general cropland. Further research and resources need to be devoted to produce region-specific crop masks that differentiate different types of crops.  

## Future Projections

Future changes in climate will have significant impacts in agriculture. In Papua New Guinea, changes in precipitation, temperature, and the frequency of hot/cold days will be a determining factor of future crop yield. Climate projections can be used to approximate the significance of these impacts.  

The WBG Climate Change Knowledge Portal [CCKP](https://climateknowledgeportal.worldbank.org/country/papua-new-guinea) provide projections of Annual number of days with Heat Index >35°C, Anomaly of Precipitation, and Anomaly of Maximum Temperature. This can be a basis for the projection of crop yield changes. Elisabeth Vogel et al. ([2019](https://iopscience.iop.org/article/10.1088/1748-9326/ab154b)) identified sensitivity of maize, soybeans, spring wheat, and rice to warm day frequency and cold night frequency. Easterling, W. E. et al. ([2007](https://pubs.giss.nasa.gov/docs/2007/2007_Easterling_ea01000b.pdf)) studied cereals, wheat, and rice sensitivity to 1°C increase of temperature in different latitude. Changes in short-term temperature extremes can also be critical if they coincide with key stages of development. Wheeler et al. ([2000](https://www.sciencedirect.com/science/article/abs/pii/S0167880900002243?via%3Dihub)) identified only a few days of extreme temperature (greater that 32°C) at the flowering stage of many crops can drastically reduce yield.  

![future-projection](./images/climag/climag-futureprojection.png)

**Figure 22.**  PNG Projections: Annual number of days with heat index > 35oC, Anomaly of precipitation, and Anomaly of Tmax in 2040 – 2059.[^1]

The maps are based on Shared Socioeconomic Pathways [(SSPs)](https://en.wikipedia.org/wiki/Shared_Socioeconomic_Pathways) Scenario 8.5 (worst scenario) for the period 2040 - 2059. Reference period: 1995 – 2014. This type of data is critical for the design of adaptation measures and long-term agriculture development plans.  

``````{admonition} Map Disclaimer
:class: dropdown
Country borders or names do not necessarily reflect the World Bank Group's official position. This map is for illustrative purposes and does not imply the expression of any opinion on the part of the World Bank, concerning the legal status of any country or territory or concerning the delimitation of frontiers or boundaries.
``````
[^1]: Reference period: 1995 – 2014. Source: https://climateknowledgeportal.worldbank.org/country/papua-new-guinea/climate-data-projections