# Automatic Identification System

## Introduction

The Automatic Identification System was originally developed by the International Maritime Organization in 2004 to prevent collisions between large vessels. This system requires all commercial ships (gross tonnage greater than 300) and passenger ships to broadcast their position and other characteristics via ground stations and satellites. The resulting data is highly complex as it includes dynamic information on ship movements (position and speed), and static information on ship characteristics and voyage-related attributes.

Although AIS was originally developed to maintain safety at sea, recent work by [IMF researchers](https://blogs.worldbank.org/opendata/using-marine-spatial-data-inform-development-work-and-public-policies) has highlighted its potential to nowcast economic statistics, with a particular focus on trade. Most relevantly, [Arslanalp, Koepke and Verschuur (2019)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4026426) conducted a study to track daily merchandise trade at the port-level in the Pacific Islands.

Our team has expanded on existing methodologies to derive key indicators for the Pacific Island ports and economic zones.

## Interactive Map 

This interactive map contains the following layers:

1. Pacific Islands Economic Zones (Source: [Pacific Data Hub](https://pacificdata.org/data/dataset/pacific-island-countries-and-territories-exclusive-economic-zones/resource/dad3f7b2-a8aa-4584-8bca-a77e16a391fe?view_id=3b20af1a-887f-4048-9204-05996042dd48))
2. Port Boundaries (Source: IMF)
3. Heatmap of AIS Messages (click on layer to display)
    > *Random 10% per buffer, aggregated by H3 resolution 12, ~154 sqm per H3*

<div id="content" style="max-width: 100%; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <iframe src="../images/interactive/ais/PacificIslandsMap.html" name="Pacific Islands Map" id="Pacific Islands Map" style="border: 0; position: absolute; top: 0; left: 0; width: 100%; height: 100%;" allowfullscreen="">
  </iframe>
</div>

## Applications 

### [Port Arrivals and Trade Volume](ais_trade.md)
### [Greenhouse Gas Emissions from Vessels](ais_emissions.md)
### [Fishing Intensity (Global Fishing Watch)](ais_fishing.md)

## Additional Resources

- [AIS Handbook, Global Working Group on Big Data for Official Statistics](https://unstats.un.org/wiki/display/AIS/Introduction)
    > Data for this analysis is available through the UN Global Platform, which also
    hosts a dedicated working group to promote the use of AIS data to derive economic
    indicators.
