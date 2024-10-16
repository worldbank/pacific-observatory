# Port Arrivals and Trade Volume

This page showcases results from our paper **Estimating Trade Volume in the Pacific Islands using Automatic Identification System (AIS)**, where we validate the use of AIS data to produce port-level statistics for the Pacific Islands. The paper is available [link]. 

This study covers Fiji, Kiribati, Marshall Islands, Micronesia, Nauru, Palau, Papua New Guinea, Samoa, Solomon Islands, Tonga, Tuvalu, and Vanuatu. The primary data sources are AIS data and ship registry from the UN Global Platform (UNGP), and global port boundaries from the {cite:t}`TrackingTradefromSpaceAnApplicationtoPacificIslandCountries` study. The period covered by this study is from January 2019 to April 2023.

We follow two existing methodologies on trade volume estimation ({cite:t}`TrackingTradefromSpaceAnApplicationtoPacificIslandCountries`; {cite:t}`Jia2019`) to estimate the cargo carried by each vessel upon arrival and departure. These papers utilize dynamic information on ship movements, static characteristics of each ship, and reported draft (depth of submergence), to estimate the amount of goods offloaded or loaded at a certain port. We find that our derived port calls data accurately capture international trade-related ships, and whilst cargo volume levels are off from official data, they can still capture variation across ports and relative trends within each port.

## Map of Ports

The map below shows the location of each port and the buffer area (22 km) used to extract AIS data.

<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <iframe src="../interactive/ais/PacificIslandsPorts.html" name="Pacific Islands Map" id="Pacific Islands Map" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen="">
  </iframe>
</div>

## Port Arrivals 

<div class="flourish-embed flourish-chart" data-src="visualisation/19836784?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19836784/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

## Trade Volume

<div class="flourish-embed flourish-chart" data-src="visualisation/19837444?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19837444/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

## Data Availability

The output data from this analysis is publicly available through the [Development Data Catalog](https://datacatalog.worldbank.org/search/dataset/0062856/Pacific%20Observatory%20Datasets?version=6).

## References

```{bibliography}
```