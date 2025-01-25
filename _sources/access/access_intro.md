# Market Access and Connectivity

Market Access can be defined as the ability to reach "destinations" (for example, cities, ports, goods, or services). In other words, it is a measure of a population's potential to access opportunities. In the context of the Pacific, market access is constrained by the region's vast distances, remoteness, and the dispersion of its islands. The region is also prone to natural disasters, which can further disrupt connectivity.

This analysis uses the latest public data to build a multi-modal network to study accessibility and connectivity in the Pacific. It is split into two components: (1) measures of land-based travel time and (2) connectivity between islands through ferry routes. As a starting point to demonstrate the methodology, we calculate travel time to major cities in the Pacific and map ferry routes between islands.

## Definition of Urban Clusters

We use gridded population data from WorldPop to identify population centers in the Pacific. Following the [Degree of Urbanization](https://human-settlement.emergency.copernicus.eu/degurbaDefinitions.php) classification, we define urban clusters as contiguous areas with total population greater than 5,000 and population density of at least 190 inhabitants per sq. km. (originally 300, adjusted to 190 for the Pacific to capture more areas).

## Friction Surface

For land-based travel, we leverage the motorized transport friction surface developed by [Weiss et al. (2020)](https://www.nature.com/articles/s41591-020-1059-1). The friction surface is a raster dataset that represents the time it takes to cross a cell in minutes. The dataset is based on roads data from OpenStreetMap and Google Maps, and incorporates additional terrain factors such as slope, land cover, and elevation. Using this data as a cost surface, we use the [GOSTnetsraster](https://github.com/worldbank/GOSTnetsraster) toolkit to estimate the shortest travel time from every pixel to the nearest city.

## Accessibility Maps

The following maps provide a baseline measure of market access. The maps show motorized travel time to the nearest urban cluster in hours.

````{tab-set}
``` {tab-item} Papua New Guinea
![Overview](../images/access/travel-time-friction-png.png)
```
``` {tab-item} Solomon Islands
![Overview](../images/access/travel-time-friction-slb.png)
```
``` {tab-item} Tonga
![Overview](../images/access/travel-time-friction-ton.png)
```
``` {tab-item} Tuvalu
![Overview](../images/access/travel-time-friction-tuv.png)
```
``` {tab-item} Vanuatu
![Overview](../images/access/travel-time-friction-vut.png)
```
````

## Interactive Maps

Because of the large geographic distances between islands, some of the islands are not visible in the static maps. The same data is displayed below with interactive maps, allowing users to zoom in and out to explore the accessibility of different islands, as well as overlaying roads and points of interest from OpenStreetMap and a satellite imagery basemap.

### Papua New Guinea
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
<iframe src="../interactive/access/travel_time_png.html" name="Micronesia" id="Micronesia" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Federated States of Micronesia
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
<iframe src="../interactive/access/travel_time_fsm.html" name="Micronesia" id="Micronesia" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Marshall Islands
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_mhl.html" name="Marshall" id="Marshall" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Nauru
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_nru.html" name="Nauru" id="Nauru" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Palau
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_plw.html" name="Palau" id="Palau" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Samoa
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_wsm.html" name="Samoa" id="Samoa" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Solomon Islands
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_slb.html" name="Solomon" id="Solomon" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Tonga
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_ton.html "name="Tonga" id="Tonga" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Tuvalu
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_tuv.html" name="Tuvalu" id="Tuvalu" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Vanuatu
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_vut.html" name="Vanuatu" id="Vanuatu" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Fiji 
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_fji.html" name="Fiji" id="Fiji" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

### Kiribati
<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/travel_time_kir.html" name="Kiribati" id="Kiribati" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

## Ferry Routes

For sea-based travel, we leverage the AIS data accessed through the UN Global Platform. We query AIS signals from vessels that are classified as **Passenger** and have local flags in the Pacific. We then filter out signals from static vessels where speed over ground is 0. This proof of concept uses AIS passenger signals from Vanuatu for the full year of 2023.

```{figure} ../images/access/ferry-vut.jpg
---
alt: AIS Signals from passenger vessels in Vanuatu
width: 100%
---
AIS Signals from passenger vessels in Vanuatu
```

### Trajectories

We apply various algorithms from [MovingPandas](https://movingpandas.readthedocs.io/en/main/) to derive ferry routes from AIS signals. First, we group the data points into collections by unique vessel identifier and consecutive timestamps. We then split these trajectories into individual trips based on a time gap of 1 hour. 

Next, we simplify the trajectories by identifying clusters of points, snapping the start and end point of each route to a given cluster. This allows us to generate a network graph of all routes between islands, where each node represents a cluster of points and each edge represents a route.

```{figure} ../images/access/ferry-vut-network.png
---
alt: Network graph of routes between islands in Vanuatu
width: 100%
---
Network graph of routes between islands in Vanuatu
```

To separate single trips (or cruises) from recurring ferries, we examine the **weight** for each network edge. In other words, the number of times a route is present in the AIS data.

<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
    <iframe src="../interactive/access/ferry-vut-network.html" name="Vanuatu Network" id="Vanuatu Network" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen=""></iframe>
</div>

In forthcoming updates, we will expand this analysis to integrate the ferry routes with the land-based travel time analysis to provide a comprehensive view of connectivity in the Pacific.