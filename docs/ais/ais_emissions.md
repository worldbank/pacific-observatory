# Greenhouse Gas Emissions from Maritime Traffic

In this research, we follow a bottom-up approach to estimate greenhouse gas emissions from vessel journeys. The methodology is based on the [Fourth International Maritime Organization (IMO) Greenhouse Gas Study (2020)](https://www.imo.org/en/ourwork/Environment/Pages/Fourth-IMO-Greenhouse-Gas-Study-2020.aspx) and was adapted by Cherryl Chico. Vessel navigation data from Automatic Identification System (AIS), and vessel specification data from Ship Register database are used to calculate emissions for the Pacific Island Countries.

## Methodology

### Theoretical Foundation

Emissions are calculated for two groups of greenhouse gas (GHG): energy-based—nitrogen oxide (NO<sub>x</sub>), methane (CH<sub>4</sub>, carbon monoxide (CO), nitrous oxide (N<sub>2</sub>O), particulate matter (PM<sub>10</sub>,PM<sub>2.5</sub> ), and non-methane volatile organic compounds (NMVOCs), and fuel-based—carbon dioxide (CO<sub>2</sub>) and sulphur oxides (SO<sub>x</sub>).  

Black carbon (BC) can either be energy- or fuel-based depending on the fuel type. Energy-based GHG is expressed as the product of emission factor and power demanded adjusted by a correction factor based on engine load (Eq. 1). For fuel-based GHG, power demanded is converted to specific fuel consumption. Emissions is calculated per hour and per engine (i.e. main engine, auxiliary engine, or boiler if available) of the vessel in operation.

```{math}
:label: my_label
Energy{-}Based\ Emission_{GHG} = \sum_E \sum_i EF_{E,GHG} \cdot P_{E,i} \cdot LCF_{E,i,GHG}
```
```{math}
:label: my_label
Energy{-}Based\ Emission_{GHG} = \sum_E \sum_i EF_{E,GHG} \cdot P_{E,i} \cdot LCF_{E,i,GHG}
```

Where
- $E$ is the vessel’s engine
- $i$ is hour
- $EF_{E,GHG}$ is the energy-based emission factor (g/kWh) for engine $E$ and gas $GHG$
- $FF_{E,GHG}$ is the fuel-based emission factor (g/kg-fuel) per for engine E and gas GHG
- $LLF_{E,i,GHG}$ is the low load adjustment factor for gas GHG given load at hour $i$
- $P_{E,i}$ is the power demanded of engine $E$ at hour $i$
- $FC_{E,i}$ is the fuel consumption of engine $E$ at hour $i$

Each of the components of equations (1) and (2) are collected data by the IMO from various literature and from their own calculations which are then reviewed per iteration of the GHG study. They are presented either as an equation, decision matrix, or reference table.

### Power Demanded

Power demanded is the power required to operate a vessel at a given speed and displacement. In the GHG study, the power demanded by the main engine is a function of the vessel’s speed and draught at any given hour. Power demanded is expressed as the product of engine load and maximum power, where engine load is derived from the admiralty formula including correction factors (CF). The correction factors are meant to increase the engine load due to weather and hull fouling, and to decrease the engine load for some large vessels where maximum speed corresponds to a lower engine load. 

```{math}
:label: my_label
P_i = Load_i \times P_{max}
```
```{math}
:label: my_label
Load_i = \left( \frac{draught_i}{draught_{design}} \right)^{\frac{2}{3}} \times \left( \frac{speed_i}{speed_{max}} \right)^3 \times CF
```

Where
- $i$ is hour
- $draught_{i/design}$ is the vessel’s draught at hour i / design draught
- $speed{i/max}$ is the vessel’s speed at hour i / maximum speed
- $CF$ is the correction factor

For the auxiliary engine and boiler, the power demanded is simplified as either a fraction of the main engine power or a fixed value according to the vessel’s type, size, and operational phase. 

Per the GHG study, engines that operate at engine load less than 20% have lower combustion efficiency and therefore higher emissions. To account for this, the load correction factor (LCF) is applied as a multiplier when engine load is less than 20% with varying values across GHG and ranges of engine load.

### Specific Fuel Consumption

Power demanded is converted to fuel consumption using a baseline specific fuel consumption (SFC) adjusted by the load correction factor (LCF). The baseline SFC is a fixed value that varies across engine type, fuel type, and year of built. The load correction factor (LCF) is a parabolic function that results in high values for both low and high inputs of engine load, and low values with engine load near 80%. LCF is only applied for oil and LNG engines for the main engine.

```{math}
:label: my_label
SFC_{E,i} = P_{E,i} SFC_{base} LCF_{i}
```

Where
- $i$ is hour
- $P_i$ is the power demanded at hour $i$
- $SFC_{base}$ is the baseline specific fuel consumption 
- $draught_{i/design}$ is the vessel’s draught at hour i / design draught
- $LCF_i$ is the load correction factor function at hour i

## Data Exploration

AIS data is extracted by Exclusive Economic Zones (EEZ) from 2019 to May 2024. The charts below show the number of unique vessels per month for each economic zone.

<div class="flourish-embed flourish-chart" data-src="visualisation/19738193?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19738193/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

For each vessel journey, we calculate the total emissions of various GHG components. The below summarizes monthly CO2 emissions by type of vessel (Cargo, Tanker, Fishing, Passenger, or Other). Toggle the area of interest to explore emissions by country.

<div class="flourish-embed flourish-chart" data-src="visualisation/19744172?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19744172/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

The following grid expresses the same data as a stacked bar chart to explore the share of emissions produced by each vessel type.

<div class="flourish-embed flourish-chart" data-src="visualisation/19757891?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19757891/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

Similarly, the tree map below shows the annual composition of CO2 emissions across areas and vessel types.

<div class="flourish-embed flourish-hierarchy" data-src="visualisation/19770754?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19770754/thumbnail" width="100%" alt="hierarchy visualization" /></noscript></div>

We also calculate emissions for other GHG and pollutants, including Particulate Matter and Methane. Each line in this chart represents total monthly emissions for a specific pollutant.

<div class="flourish-embed flourish-chart" data-src="visualisation/19771256?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19771256/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

## Data Availability

The output dataset contains **monthly GHG emissions disaggregated by vessel type, status of operation and country**. The dataset is publicly available through the [Development Data Catalog](https://datacatalog.worldbank.org/search/dataset/0062856/Pacific%20Observatory%20Datasets?version=6). You can download the data as an excel spreadsheet using this [link](https://datacatalogfiles.worldbank.org/ddh-published/0062856/DR0094580/Emissions%20Pacific%20201901_202405%20(pivot).xlsx?versionId=2024-10-10T18:42:36.1537471Z).

## Metadata

The dataset contains the following fields.

| Field                   | Definition                                                                                              |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| Country                 | Indonesia                                                                                               |
| year                    | year                                                                                                    |
| month                   | month                                                                                                   |
| type                    | Type 1&2 - with Ship Register data, Type 3 - without Ship Register data                                 |
| _vessel_group_ais       | "Cargo, Tanker, Fishing, Passenger, Others Type 3 is based on vessel_type field in ais, Type 1&2 based on Ship Register" |
| _vessel_class_no        | Type 1&2 only, follows IMO grouping                                                                     |
| _vessel_class           | Type 1&2 only, follows IMO grouping                                                                     |
| _w_fishing              | Flag to indicate if the hourly activity is a fishing activity according to GFW data                     |
| _op_phase               | At Berth, Anchored, Maneouvring, Sea (increasing speed)                                                 |
| count_vessel            | Count of unique vessels                                                                                 |
| count_vessel_day        | Total number of days of activity for all vessels                                                        |
| _missing_hours          | Total number of hours of activity interpolated due to missing AIS data                                  |
| _total_hours            | Total hours of activity                                                                                 |
| _ch4_energy             | Main engine emission for CH4 (Methane)                                                                  |
| _co_energy              | Main engine emission for CO (Carbon Monoxide)                                                           |
| _n2o_energy             | Main engine emission for N2O (Nitrous Oxide)                                                            |
| _nmvoc_energy           | Main engine emission for NMVOC (Non-Methane Volatile Organic Compounds)                                 |
| _pm10_energy            | Main engine emission for PM10 (Particulate Matter)                                                      |
| _pm25_energy            | Main engine emission for PM2.5 (Particulate Matter)                                                     |
| _nox_energy             | Main engine emission for NOx (Nitrogen Oxide)                                                           |
| _bc_energy              | Main engine emission for BC (Black Carbon)                                                              |
| _ch4_energy_pilot       | Pilot fuel emission for CH4 (Methane)                                                                   |
| _co_energy_pilot        | Pilot fuel emission for CO (Carbon Monoxide)                                                            |
| _n2o_energy_pilot       | Pilot fuel emission for N2O (Nitrous Oxide)                                                             |
| _nmvoc_energy_pilot     | Pilot fuel emission for NMVOC (Non-Methane Volatile Organic Compounds)                                  |
| _pm10_energy_pilot      | Pilot fuel emission for PM10 (Particulate Matter)                                                       |
| _pm25_energy_pilot      | Pilot fuel emission for PM2.5 (Particulate Matter)                                                      |
| _nox_energy_pilot       | Pilot fuel emission for NOx (Nitrogen Oxide)                                                            |
| _bc_energy_pilot        | Pilot fuel emission for BC (Black Carbon)                                                               |
| _ab_ch4_energy          | Auxiliary Boiler emission for CH4 (Methane)                                                             |
| _ab_co_energy           | Auxiliary Boiler emission for CO (Carbon Monoxide)                                                      |
| _ab_n2o_energy          | Auxiliary Boiler emission for N2O (Nitrous Oxide)                                                       |
| _ab_nmvoc_energy        | Auxiliary Boiler emission for NMVOC (Non-Methane Volatile Organic Compounds)                            |
| _ab_pm10_energy         | Auxiliary Boiler emission for PM10 (Particulate Matter)                                                 |
| _ab_pm25_energy         | Auxiliary Boiler emission for PM2.5 (Particulate Matter)                                                |
| _ab_nox_energy          | Auxiliary Boiler emission for NOx (Nitrogen Oxide)                                                      |
| _ab_bc_energy           | Auxiliary Boiler emission for BC (Black Carbon)                                                         |
| _ae_ch4_energy          | Auxiliary engine emission for CH4 (Methane)                                                             |
| _ae_co_energy           | Auxiliary engine emission for CO (Carbon Monoxide)                                                      |
| _ae_n2o_energy          | Auxiliary engine emission for N2O (Nitrous Oxide)                                                       |
| _ae_nmvoc_energy        | Auxiliary engine emission for NMVOC (Non-Methane Volatile Organic Compounds)                            |
| _ae_pm10_energy         | Auxiliary engine emission for PM10 (Particulate Matter)                                                 |
| _ae_pm25_energy         | Auxiliary engine emission for PM2.5 (Particulate Matter)                                                |
| _ae_nox_energy          | Auxiliary engine emission for NOx (Nitrogen Oxide)                                                      |
| _ae_bc_energy           | Auxiliary engine emission for BC (Black Carbon)                                                         |
| _co2_fuel               | Main engine emission for CO2 (Carbon Dioxide)                                                           |
| _sox_fuel               | Main engine emission for SOx (Sulphur Oxide)                                                            |
| _bc_fuel                | Main engine emission for BC (Black Carbon)                                                              |
| _co2_fuel_pilot         | Pilot fuel emission for CO2 (Carbon Dioxide)                                                            |
| _sox_fuel_pilot         | Pilot fuel emission for SOx (Sulphur Oxide)                                                             |
| _bc_fuel_pilot          | Pilot fuel emission for BC (Black Carbon)                                                               |
| _ab_co2_fuel            | Auxiliary Boiler emission for CO2 (Carbon Dioxide)                                                      |
| _ab_sox_fuel            | Auxiliary Boiler emission for SOx (Sulphur Oxide)                                                       |
| _ab_bc_fuel             | Auxiliary Boiler emission for BC (Black Carbon)                                                         |
| _ae_co2_fuel            | Auxiliary engine emission for CO2 (Carbon Dioxide)                                                      |
| _ae_sox_fuel            | Auxiliary engine emission for SOx (Sulphur Oxide)                                                       |
| _ae_bc_fuel             | Auxiliary engine emission for BC (Black Carbon)                                                         |
| _ch4_e                  | Total emission for CH4 (Methane)                                                                        |
| _co_e                   | Total emission for CO (Carbon Monoxide)                                                                 |
| _n2o_e                  | Total emission for N2O (Nitrous Oxide)                                                                  |
| _nmvoc_e                | Total emission for NMVOC (Non-Methane Volatile Organic Compounds)                                       |
| _pm10_e                 | Total emission for PM10 (Particulate Matter)                                                            |
| _pm25_e                 | Total emission for PM2.5 (Particulate Matter)                                                           |
| _nox_e                  | Total emission for NOx (Nitrogen Oxide)                                                                 |
| _bc_e                   | Total emission for BC (Black Carbon)                                                                    |
| _co2_f                  | Total emission for CO2 (Carbon Dioxide)                                                                 |
| _sox_f                  | Total emission for SOx (Sulphur Oxide)                                                                  |
| _bc_f                   | Total emission for BC (Black Carbon)                                                                    |