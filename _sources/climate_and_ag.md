# Climate and Agriculture Monitoring in the Pacific Island Countries

Weather conditions and climate variations have profound impacts on agriculture, water resources and on the socioeconomic opportunities and adaptations of a region. Populations in the Pacific Island Countries (PIC) are at disproportionately higher risk of adverse consequences from global warming. Current impacts include increasing droughts and water scarcity, coastal flooding and erosion, and changes in rainfall that affect food production (IPCC 2018). At the same time, there is wealth of underutilized satellite data that can be useful to monitor climate events and provide insights for better preparedness and mitigation strategies. 

Climate indices with high resolution have long been very limited, for example Standardized Precipitation Evapotranspiration Index (SPEI) only available at 0.5 deg (~ 55 km) resolution for global coverage. This often leave small island countries like Pacific not captured well. Since 2014, a number of high gridded climate have been produced. GOST team is able to calculate climate indices with spatial resolution ranging from 11 to 4 km. It is interesting to unlock access to climate datasets and investigate how the changing climate is affecting irrigated and dryland agriculture in the Pacific Island Countries (PICs) via this activity. 

Climate data is a critical resource to help us prepare for and address the challenges of a changing environment. Through a better understanding of past climate conditions, local and regional climate variability and how current conditions compare to the past, we can assess the status of water supplies, agricultural production, and other natural resources.

Weather and climate affect not only agriculture but recreation, transportation, energy supply and demand, and many aspects of resource management. Climate information is important for short- and long-term planning, operational decision making, development of adaptive infrastructure and the management of climate-sensitive risks. Through diverse means of climate monitoring and multiple channels of information delivery, this activity will help the citizens of PIC see and understand how climate affects their livelihoods.

These following examples use low to medium spatial resolution Earth Observation (EO) data to monitor hydro-meteorological condition and growing seasons.


## Climate Variability

Climate variability directly influences many aspects of food and nutrition security, particularly food availability and access. Variation in rainfall is a common element of many natural disasters – droughts, floods, typhoons and tsunamis – and is influenced by global, regional and/or local factors. 

Global climate factors including El Niño-Southern Oscillation (ENSO); regional factors include the Madden-Julian Oscillation, West Pacific Gradient (WPG) and fluctuations in the sea surface temperature (SST) of the Pacific Ocean; and local factors can include elevation, island position, the circulation of land and sea breezes, and land cover.

The level of climate risk is measured based on the strength of ENSO signal on rainfall variability using correlation analysis. This approach is applied because production loss of food crops in Southeast Asia and the Pacific is closely associated with the ENSO phenomena (Naylor et al, [2001](https://doi.org/10.1023/A:1010662115348), [2007](http://dx.doi.org/10.1073/pnas.0701825104)). Anderson ([2018](https://doi.org/10.1016/j.agrformet.2018.07.023))  specifically indicates ENSO poses risks to crop production in greater [Pacific Basin region](https://en.wikipedia.org/wiki/Pacific_Rim). El Nino years is normally associated with drought years, while La-Nina is often related to wet years which can cause flood hazards. The correlation analysis is applied to monthly rainfall anomaly and sea surface temperature anomaly in in the in four NINO regions along the equator:
* Niño 1 (80°-90°W and 5°-10°S)
* Niño 2 (80°-90°W and 0°-5°S)
* Niño 3 (90°-150°W and 5°N-5°S)
* Niño 4 (150°-160°E and 5°N-5°S)

![nino](./images/climag/climag-ninoregion.jpeg)

**Figure 1.** NINO regions. Source: https://www.weather.gov/jetstream/enso

The NINO region is optimal for monitoring ENSO and its impacts, while the WPG is measured as the difference in SST between the NINO4 region and the West Pacific region. When the WP is warm during La Nina events, the changes across the globe can be extreme.

Simple regression applied to indicate the correlation between rainfall anomaly in each area to anomaly of SST in the Pacific Ocean which represent ENSO signals.

`Y = aX + b`, where: `Y` = Rainfall anomaly, `b` = `Y` intercept, `a` = Slope and `X` = SST anomaly

![nino34](./images/climag/climag-pci-precip-sst.png)

**Figure 2.** General sensitivity of rainfall to SST changes in NINO3.4 region

Slope map shows the changes in monthly rainfall likely to result from a 1°C change in SST. The map demonstrates the change in rainfall associated with a one degree decrease in SST in NINO-3.4 region. Red highlighted areas on the map such as Tuvalu, Kiribati, Nauru, and partly New Britain and Bougainville Island of PNG would be severely affected or experience >=10 - 50 mm below normal rainfall in the respective month by 1°C change in SST. In contrast, dark blue highlighted areas would experience >50mm higher monthly rainfall.

ENSO signals used to be the key indicators for agriculture production in some areas. However negative impacts of the signals to production have been reduced with a wide range of adaptations like improvement of irrigation facilities, innovations of drought/flood crop tolerant varieties. Still, the signals remain helpful for hydro-meteorological disasters forecast.


## Climate Monitoring

This involves data of near real-time monitoring of satellite derived precipitation, temperature, evapotranspiration and vegetation indexes. The analysis allows early detection of water stress conditions of vegetation and monitoring of derived phenological parameters.

Now let’s talk about how we can utilize EO data to do climate monitoring for different time period.
1. Monthly seasonal, for planning and scenario development.
2. Daily and forecast, for early warning, disaster preparedness and response, and seasonal planning.
3. Forecast, for early warning early action, and seasonal planning.

### Monthly and Seasonal

The Standardized Precipitation-Evapotranspiration Index (SPEI) is an established indicator to detect, monitor, and analyze droughts. The SPEI considers how various climate indicators (precipitation, evapotranspiration, temperature) relate to normal conditions and can be calculated according to different temporal scales. The multi-scalar character of this indicator makes it a suitable proxy to identify dry and wet conditions related to soil moisture, which can have significant impacts on agriculture. 

![spei-wet](./images/climag/climag-png-spei-wet.png)

**Figure 3.** Wet condition

Figure 3 and Figure 4 indicate total area (in percentage) of a country or admin boundary that experience certain category of SPEI (dryness or wetness) monthly. For example, the above Figure informed that on Dec 2020 there were more than 75% of the country experienced wetness, only about 10% are under normal condition, and 25% of the area were exceptionally wet.

When considering country averages, Papua New Guinea has been considered wet in the last 20 years, but ENSO signal strikes a significant dry period during 2015-2016.

![spei-dry](./images/climag/climag-png-spei-dry.png)

**Figure 4.** Dry condition

Showing the inverse of Figure 3, Figure 4 indicates months with dryer than usual climate for example during the strong El Nino of 2015-2016. These figures are interlinked with Figure 1 and provide the information of ENSO signal. Compared to Figure 2, these figures provide more explicit seasonal pattern or time frame. Like slow onset disasters monitoring. We can learn how the dry or wet situation are evolving month-by-month, year-by-year.

The map below compares the SPEI monthly indicator in two different periods: December 2015 for Strong El Nino and December 2020 for Moderate La Nina.

![spei-wet](./images/climag/climag-png-spei-maps.png)

**Figure 5.** SPEI 12-months

Long-term historical information is a key for us to understand what happened in the past and see climate variabilities in the areas.
60-years SPEI data is available to better understand and captures the main impact of increased temperatures on water demand.

````{tab-set}
``` {tab-item} Papua New Guinea
![Overview](./images/climate/spei12/Papua-New-Guinea.jpeg)
```
``` {tab-item} Federated States of Micronesia
![Overview](./images/climate/spei12/Federated-States-of-Micronesia.jpeg)
```
``` {tab-item} Fiji
![Overview](./images/climate/spei12/Fiji.jpeg)
```
``` {tab-item} Kiribati
![Overview](./images/climate/spei12/Kiribati.jpeg)
```
``` {tab-item} Marshall Islands
![Overview](./images/climate/spei12/Marshall-Islands.jpeg)
```
``` {tab-item} Nauru
![Overview](./images/climate/spei12/Nauru.jpeg)
```
``` {tab-item} Palau
![Overview](./images/climate/spei12/Palau.jpeg)
```
``` {tab-item} Samoa
![Overview](./images/climate/spei12/Samoa.jpeg)
```
``` {tab-item} Solomon Islands
![Overview](./images/climate/spei12/Solomon-Islands.jpeg)
```
``` {tab-item} Tonga
![Overview](./images/climate/spei12/Kingdom-of-Tonga.jpeg)
```
``` {tab-item} Tuvalu
![Overview](./images/climate/spei12/Tuvalu.jpeg)
```
``` {tab-item} Vanuatu
![Overview](./images/climate/spei12/Vanuatu.jpeg)
```
````


### Daily

This section explores daily extreme rainfall based on satellite precipitation estimates. Our objective here is to showcase how we can utilize daily weather data to inform early warning systems and disaster response policies.

![extreme-rain](./images/climag/climag-png-extreme-rain.png)

**Figure 6.** Extreme rainfall

There are at least five questions that can be explored with this type of data:
1. Availability monitoring and forecast data on daily extreme rainfall is important to support early warning and anticipatory actions.
2. Will it trigger a landslide?
3. Which transportation network will be affected?
4. How many population and cropland will be affected by extreme rainfall in the next 3 days?
5. Which area is in early planting and will be damaged?

Another high-frequency indicator of meteorological is maximum consecutive dry days (CDD). In its simplest form, this index can be described by a lack of precipitation (number of consecutive days with < 1 mm of rain). CDD is updated on daily basis and can serve as an effective measure of extreme events and seasonal droughts.

![max-cdd](./images/climag/climag-fiji-max-cdd.png)

**Figure 7.** Maximum consecutive dry days in 2021

### Forecast

[Subseasonal forecasts](http://iridl.ldeo.columbia.edu/maproom/Global/ForecastsS2S/index.html) and [Seasonal forecast](http://iridl.ldeo.columbia.edu/maproom/Global/Forecasts/index.html) of precipitation and temperature are coming from International Research Institute (IRI) of Columbia University. 

The forecasts may allow delivering relevant information about key climate characteristics such as the timing of the onset of a rainy season for agriculture, the risk of extreme rainfall events or heat waves in regard to public health. 

Color scales are colors indicating that the distribution of the forecast tends towards drier (shades of brown) or wetter (shades of blue) conditions than normal (moccasin).

1.	Short-term/Sub-seasonal Forecast: Optimum planting/harvest potential

	Sub-seasonal forecasts are known to focus on prediction of key variables such as temperature or precipitation at weekly up to 1 month interval.

	![subx-precip](./images/climag/climag-subx-precip.png)

	**Figure 8.** Sub-seasonal Forecast Precipitation. Source: IRI

	Historical records of planting in combination with temperature and rainfall forecasts are helpful to draw a recommendation on optimum planting/harvest potential. Weather forecasts released during the 2nd or 3rd planting season allow us to plan optimum yield, meaning that we can identify what type of crops (main or secondary crops) grow optimally for the forecasted precipitation level, which area can and cannot grow secondary crops, distribution of seeds, and other relevant planning.

	![subx-temp](./images/climag/climag-subx-temp.png)

	**Figure 9.** Sub-seasonal Forecast Temperature. Source: IRI

2.	Seasonal Forecast: Opportunities during climate extreme events

	Seasonal forecasts provides longer interval compared to sub-seasonal forecasts, it usually available up to 7 months. Accuracy of sub-seasonal forecast is slightly higher than seasonal as is is predicting less far into the future. It is scientifically challenging to maintain accuracy level at longer timeframe.

	![seasonal-precip](./images/climag/climag-seasonal-precip.png)

	**Figure 10.** Seasonal Forecast Precipitation. Source: IRI

	Seasonal forecast provides prediction of weather (rainfall) throughout the season. In combination with sub-seasonal forecasts, such information is necessary for improving the Planting Index and optimising harvested areas. As an example, if a certain planted area is damaged by flood/drought, we are able to better plan replantation programs by taking into account the information from long-term forecasts. If the rainfall in the longer term allows, replantation programs can be initiated.
	
	![seasonal-temp](./images/climag/climag-seasonal-temp.png)

	**Figure 11.** Seasonal Forecast Temperature. Source: IRI


### Cyclone Season

Currently we only have historical cyclones track. Yet, this informed us if certain areas are vulnerable to agriculture production loss due to extreme rainfall caused by cyclones. The following parts of this section provide description of cyclones occur in Pacific and their timeline passing Southern and Western Pacific Ocean. 

Traditionally, areas of tropical cyclone formation are divided into seven basins. These include the north Atlantic Ocean, the eastern and western parts of the northern Pacific Ocean, the southwestern Pacific, the southwestern and southeastern Indian Oceans, and the northern Indian Ocean (Arabian Sea and the Bay of Bengal). 

![tc-regions](./images/climag/climag-tc-regions.png)

**Figure 12.** Tropical cyclone centers and regions. Source: https://en.wikipedia.org/wiki/File:Tropical_Cyclone_Centers_and_Regions.png 

1. Western Pacific Ocean

	The West Pacific Ocean is the most active basin on the planet, accounting for one-third of all tropical cyclone activity. Annually, an average of 25.7 tropical cyclones in the basin acquire tropical storm strength or greater; also, an average of 16 typhoons occurred each year during the 1968–1989 period. The basin sees activity year-round; however, tropical activity is at its minimum in February and March.

	![tc-north](./images/climag/climag-pci-tc-north.jpeg)

	**Figure 13.** Tracks of all tropical cyclones in the northwestern Pacific Ocean between 1980 and 2005. The vertical line to the right is the International Date Line. Source: https://en.wikipedia.org/wiki/Tropical_cyclone_basins

2. South Pacific Ocean

	Tropical Cyclones that develop within this basin generally affect countries to the west of the dateline, though during years of the warm phase of El Niño–Southern Oscillation cyclones have been known to develop to the east of the dateline near French Polynesia. On average the basin sees nine tropical cyclones annually with about half of them becoming severe tropical cyclones.

	![tc-south](./images/climag/climag-pci-tc-south.jpeg)

	**Figure 14.** Tracks of all tropical cyclones in the southwestern Pacific Ocean between 1980 and 2005. Source: https://en.wikipedia.org/wiki/Tropical_cyclone_basins

The below picture indicates that during December to May cyclone events occur mostly in South Pacific Ocean, and from June to December most cyclone events happen in West Pacific Ocean.

![tc-2019](./images/climag/climag-tc-2019.png)

**Figure 15.** Tropical cyclone happen in 2019. Source: https://upload.wikimedia.org/wikipedia/en/timeline/4dea2f730b024e57a1db72e8dc62f515.png 

## Agriculture Monitoring

Climate and vegetation data sourced from remote sensing satellites (earth observation – EO) are widely used for agricultural monitoring, especially on the growing season. Most of the usage is focused on medium-low resolution data because it is associated with long-term data availability.

These data provide useful information for:

1. Providing early warning when climate shocks occur against food security.

2. Contextual analysis (food security analysis:food access, availability and utilizations) needed for planning interventions, for example: market operations when crop scarcity occurs. 

	* Food access: market accessibility, extreme events (disaster, war)  hindering the transportation

	* Food availability: cultivation and harvested areas, utilization for domestic consumption or else.

3. Availability of cropland area for spring crop planting possibly damaged during conflict will help the team to assess the social, poverty, and economic impacts of climate change.


### Ideal remote sensing data characteristics for vegetation monitoring

Operational data production – routinely produce the same data products at a set time interval.

* Example: production a vegetation condition map each month.

Anomaly, Percent of Normal, Change, or Ranking Maps

* Provide historical context of how current conditions compare to the historical conditions for a specific location and time during the year.

* Easier to differentiate moderate, severe, and extreme drought events.

Data easily accessible and in multiple formats

* Digital data in analysis using GIS and computers

* Graphical maps that can be downloaded and printed for visual analysis

### Vegetation Index

The Enhanced Vegetation Index (EVI) is an 'optimized' index designed to enhance the vegetation signal with improved sensitivity in high biomass regions and improved vegetation monitoring through a de-coupling of the canopy background signal and a reduction in atmosphere influences. 

![EVI](./images/climag/climag-evi-2021.png)

**Figure 16.** MODIS EVI, 2021

Whereas the Normalized Difference Vegetation Index (NDVI) is chlorophyll sensitive, the EVI is more responsive to canopy structural variations, including leaf area index (LAI), canopy type, plant physiognomy, and canopy architecture.

![NDVI](./images/climag/climag-ndvi-2021.png)

**Figure 17.** MODIS NDVI, 2021


### Methodology

This is how remote sensing data could be used to monitor the crop growing season. Working example based on areas where the majority of cropland is paddy This approach required a crop type mask and moderate resolution time series Vegetation Indices (VI) is needed to do the monitoring. High resolution and frequent data might be useful to monitor crop who doesn't have clear growing season pattern.

For this example, we use MODIS MOD13Q1 data, available at 250m spatial resolution and 16-days of temporal resolution.

![TIMESAT-gs](./images/climag/climag-growing-season.png)

**Figure 18.** Growing season

State of planting and harvesting estimates were determined by importing Vegetation Indices (VI) data into [TIMESAT](http://web.nateko.lu.se/timesat/timesat.asp) – a program for analyzing time-series satellite sensor data. TIMESAT conducts pixel-by-pixel classification of satellite images to determine whether planting has started or not. This process was followed for all of areas over multiple years in order to evaluate current planting vis-à-vis historical years from 2003 - 2021 (case using MODIS VI).

![TIMESAT](./images/climag/climag-timesat-parameters.png)

**Figure 19.** TIMESAT Parameters

Some of the seasonality parameters generated in TIMESAT: (a) beginning of season, (b) end of season, (c) length of season, (d) base value, (e) time of middle of season, (f) maximum value, (g) amplitude, (h) small integrated value, (h+i) large integrated value.

The blue line is the real EVI value and red is EVI value after smoothing. The following figure shows the differences in EVI that have not and have been smoothing. 

Phenological events are sensitive to climate variation. Therefore, phenology data provide important baseline information for assessment of ecological trends and detection of climate change impacts on multiple scales.

These phenological parameters are related to the seasonal vegetation productivity, by also considering both agricultural production and available biomass. Comparing their current values with the long-term average, minimum and maximum VI time-series, helps to better understand the performances of the considered vegetative season and its expected productivity.

### Growing Season

Information on the onset of planting seasons (and harvest time) are relevant for decision makers like to see.

![TIMESAT-sos](./images/climag/climag-timesat-sos.png)

**Figure 20.** Beginning of Season.

The map informs us on the crop planting status.

1. How's the crop planting progress?
2. How many districts are behind in planting?
	* This is also will trigger another question, if there is a delay in some district, should government do planting acceleration?
3. How many hectares crop area that available for next planting?
4. Are the current harvest enough for domestic consumption?

Decision makers also need this kind of seasonal monitoring and data triangulation for better result and information to decide

1. Planting potential for the next 3-months, this is related to distribution of agriculture inputs;
2. Mobilization of extension workers for monitoring and preparing relevant strategy e.g drought/flood anticipation-adjust irrigation system, pest/disease infestation-pest control to avoid crop failure, reservoir readiness for planting season;
3. Prepare relevant policy recommendation: assess on going situation, harvest estimate, price protection, etc

This information is necessary for both policy makers and those who is directly involved in crop production (farmers, rural business, etc). Negative consequences can be anticipated months ahead and distribution of resources is focused on potential areas of planting.

Other potential analysis is also related with the mitigation and adaptation of agriculture sector to climate change, like emission from agriculture land etc.

### Limitations and Assumptions

* Getting VI data with good quality for all period are challenging (pixels covered with cloud, snow/ice, aerosol quantity, shadow) for optic data (MODIS). Radar VI is a good alternative for this.

* The analysis of cultivated area year by year are varies, due to MODIS data quality.

* Crop type is not described, so the seasonal parameters are for general cropland.

* This value may not represent for smaller cropland. 

* Presented result are only based on publicly available data on the internet.


## Future Projections

This section is about the future climate projection and it's impact on agriculture, with the case on Change of crop yield due to changing precipitation, temperature, and frequency of hot/cold days in Papua New Guinea.

The WBG Climate Change Knowledge Portal [CCKP](https://climateknowledgeportal.worldbank.org/country/papua-new-guinea) provide projections of Annual number of days with Heat Index >35°C, Anomaly of Precipitation, and Anomaly of Maximum Temperature.

This can be a basis for the projection of crop yield changes. Elisabeth Vogel et al. ([2019](https://iopscience.iop.org/article/10.1088/1748-9326/ab154b)) identified sensitivity of maize, soybeans, spring wheat, and rice to warm day frequency and cold night frequency. Easterling, W. E. et al. ([2007](https://pubs.giss.nasa.gov/docs/2007/2007_Easterling_ea01000b.pdf)) studied cereals, wheat, and rice sensitivity to 1°C increase of temperature in different latitude. Changes in short-term temperature extremes can also be critical, if they coincide with key stages of development. Wheeler et al. ([2000](https://www.sciencedirect.com/science/article/abs/pii/S0167880900002243?via%3Dihub)) identified only a few days of extreme temperature (greater that 32°C) at the flowering stage of many crops can drastically reduce yield

![future-projection](./images/climag/climag-futureprojection.png)

**Figure 21.** PNG Projections: Annual number of days with heat index > 35oC, Anomaly of precipitation, and Anomaly of Tmax in 2040 – 2059.[^1]

The maps are based on Shared Socioeconomic Pathways [(SSPs)](https://en.wikipedia.org/wiki/Shared_Socioeconomic_Pathways) Scenario 8.5 (worst scenario) for the period 2040 - 2059.

This data allow us to identify relevant adaptation measure or longterm agriculture development plan.

``````{admonition} Map Disclaimer
:class: dropdown
Country borders or names do not necessarily reflect the World Bank Group's official position. This map is for illustrative purposes and does not imply the expression of any opinion on the part of the World Bank, concerning the legal status of any country or territory or concerning the delimitation of frontiers or boundaries.
``````

[^1]: Reference period: 1995 – 2014. Source: https://climateknowledgeportal.worldbank.org/country/papua-new-guinea/climate-data-projections