# Climate Database

Climate change poses an existential threat to many islands in the Pacific. Small island states in the region are increasingly vulnerable to extreme rainfall events, cyclones, changes in ocean circulation, and rising sea level. Climate data is a critical resource to help us prepare for and address the challenges of a changing environment. However, these datasets can be difficult to work with due to technical characteristics of the raw data. They are often stored in complex time-series grid formats such as netcdf. Additionally, global climate datasets are typically produced at coarse spatial resolutions (~55 km), making them unsuitable to study climate dynamics in small island states.

The Global Operations Support Team (GOST) has developed tools to process a suite of medium resolution climate datasets (10 to 5 km), producing monthly and daily raster files (geotiffs) for each climate indicator. This processing toolset was developed by Benny Istanto, and continues to be expanded as it informs various knowledge products and initiatives, including CCDRs and the Pacific Observatory. To learn more about the underlying source data and how each index is constructed, please refer to its [documentation pages](https://bennyistanto.github.io/gost-climate/intro.html).

## Zonal statistics

The team has calculated statistics (max, mean, median, standard deviation) for each administrative level-1 area and every timestep available. Sub-national boundaries for selected Pacific Island Countries were retrieved from the [Pacific Community PopGIS portals](https://sdd.spc.int/mapping-popgis) and, where not available, from UN OCHA via the Humanitarian Data Exchange. The script used to calculate these statistics is available in this repository.

### Output table

The output dataset can be accessed via the following Development Data Hub [entry](https://datacatalog.worldbank.org/int/search/dataset/0062856).

The output table contains monthly statistics for 131 areas across 12 countries (Papua New Guinea, Federated States of Micronesia, Fiji, Kiribati, Marshall Islands, Nauru, Palau, Samoa, Solomon Islands, Tonga, Tuvalu, Vanuatu).

The time coverage varies by indicator but extends from January 1958 to December 2021.

## Metadata

:::{note}
*Admin variables*  
**index**: Unique identifier for each area  
**ADM0_NAME**: Country name  
**ADM0_PCODE**: Country code  
**ADM1_NAME**: Administrative name  
**ADM1_PCODE**: Administrative code from original source  
**year**  
**month**  
**date**: YYYYMM  

*List of variables*  
**spi**: Standardized Precipitation Index  
**spei**: Standardized Precipitation-Evapotranspiration Index  
**cdd**: Consecutive dry days  
**cwd**: Consecutive wet days  
**drydays**: Number of dry days  
**wetdays** Number of wet days  

*Rainfall thresholds* (for cdd, cwd, drydays, wetdays)  
**1mm**: 1 millimeters of rainfall per day.  
**5mm**: 5 millimeters of rainfall per day.  

*List of zonal statistics*   
**max**: Maximum  
**mean**: Mean value  
**std**: Standard deviation  
**median**: Median value  

*Variable name example*: variable_parameter_zonal statistic  
**Variable name**: spi03_median  
**Description**: Standardized precipitation index, 3-month window, median value  
:::

## Visualization

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

## Variable Descriptions

### Standardized Precipitation Index

The Standardized Precipitation Index ([SPI](https://library.wmo.int/doc_num.php?explnum_id=7768)) is a normalized index representing the probability of occurrence of an observed rainfall amount when compared with the rainfall climatology over a long-term period. This long-term record is fitted to a probability distribution, which is then transformed into a normal distribution so that the mean SPI for the location and desired period is zero.  

Negative SPI values represent rainfall deficit and less than median precipitation (Dry), starts when the SPI value is equal or below -1.0. Whereas positive SPI values indicate rainfall surplus and greater than median precipitation (Wet), starts when the SPI value is equal or above 1.0, and ends when the value becomes negative.

### Standardized Precipitation-Evapotranspiration Index

The [SPEI](https://spei.csic.es) is an extension of the widely used SPI. The SPEI is designed to take into account both `precipitation` and `potential evapotranspiration` (PET) in determining drought. Thus, unlike the SPI, the SPEI captures the main impact of increased temperatures on water demand.  

The SPEI can measure drought severity according to its intensity and duration, and can identify the onset and end of drought episodes. The SPEI allows comparison of drought severity through time and space, since it can be calculated over a wide range of climates, as can the SPI.  

The idea behind the SPEI is to compare the highest possible evapotranspiration (what we call the evaporative demand by the atmosphere) with the current water availability. Thus, precipitation (accumulated over a period of time) in the SPEI stands for the water availability, while ETo stands for the atmospheric water demand.  

Negative SPEI values represent rainfall deficit and less than median precipitation, and high potential epotranspiration (Dry), starts when the SPEI value is equal or below -1.0. Whereas positive SPEI values indicate rainfall surplus and greater than median precipitation, and low potential epotranspiration (Wet), starts when the SPEI value is equal or above 1.0, and ends when the value becomes negative.  

### Consecutive Dry Days

The number of consecutive dry days (CDD) is the largest number of consecutive days with daily precipitation amount less than 1 mm (or depending on the rain days criteria of the country), within a certain time. Usually the process counts the number of days in the past 90 days to measure the drought level.  

### Consecutive Wet Days

The number of consecutive wet days (CWD) is similar to the above CDD, the largest number of consecutive days with daily precipitation amount more than 1 mm (or depend on the rain days criteria of the country), within a certain time. Usually the process counts the number of days in the past 90 days to measure the wet level.  

### Dry Days

The number of dry days (DD) is the largest number of days with daily precipitation amount less than 1 mm (or depending on the rain days criteria of the country), within a certain time. Usually the process counts the number of days within a year to measure the dry condition.  

### Wet Days

The number of wet days (DD) is the largest number of days with daily precipitation amount more than 1 mm (or depending on the rain days criteria of the country), within a certain time. Usually the process counts the number of days within a year to measure the wet condition.  