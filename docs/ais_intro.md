# Automatic Identification System

## Introduction

The Automatic Identification System was originally developed by the International Maritime Organization in 2004 to prevent collisions between large vessels. This system requires all commercial ships (gross tonnage greater than 300) and passenger ships to broadcast their position and other characteristics via ground stations and satellites. The resulting data is highly complex as it includes dynamic information on ship movements (position and speed), and static information on ship characteristics and voyage-related attributes.

Although AIS was originally developed to maintain safety at sea, recent work by [IMF researchers](https://blogs.worldbank.org/opendata/using-marine-spatial-data-inform-development-work-and-public-policies) has highlighted its potential to nowcast economic statistics, with a particular focus on trade. Most relevantly, [Arslanalp, Koepke and Verschuur (2019)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4026426) conducted a study to track daily merchandise trade at the port-level in the Pacific Islands.

This branch of work will build on these initiatives by adapting and improving methodologies to derive trade and fishing statistics for the Pacific Island Countries (PICs).

## Data Visualization

These interactive maps were generated with the following layers:

1. 22KM square boundary (buffer) for port point
2. IMF defined port boundaries
3. 2019 AIS Heatmap (random 10% per buffer, aggregated by H3 resolution 12, ~154 sqm per H3)

Set-up

- UNGP Platform: Ocean Spark / adb kernel OR
- UNGP Platform: Data Mechanics / cherryl kernel

Pacific Island Countries

````{tab-set}
``` {tab-item} Federated States of Micronesia
<div id= "content">
<iframe src="interactive/ais/Micronesia2019.html" name="Micronesia" id="Micronesia" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
``` 
``` {tab-item} Fiji 
No data prep yet
``` 
```{tab-item} Kiribati
<div id= "content">
    <iframe src="interactive/ais/Kiribati2019.html" name="Kiribati" id="Kiribati" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Marshall Islands
<div id= "content">
    <iframe src="interactive/ais/Marshall-Islands2019.html" name="Marshall" id="Marshall" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Nauru
<div id= "content">
    <iframe src="interactive/ais/Nauru2019.html" name="Nauru" id="Nauru" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Palau
<div id= "content">
    <iframe src="interactive/ais/Palau2019.html" name="Palau" id="Palau" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Papua New Guinea
No data prep yet
```
```{tab-item} Samoa
<div id= "content">
    <iframe src="interactive/ais/Samoa2019.html" name="Samoa" id="Samoa" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Solomon Islands
<div id= "content">
    <iframe src="interactive/ais/SolomonIslands2019.html" name="Solomon" id="Solomon" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Tonga
<div id= "content">
    <iframe src="interactive/ais/Tonga2019.html "name="Tonga" id="Tonga" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Tuvalu
<div id= "content">
    <iframe src="interactive/ais/Tuvalu2019.html" name="Tuvalu" id="Tuvalu" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
```{tab-item} Vanuatu
<div id= "content">
    <iframe src="interactive/ais/Vanuatu2019.html" name="Vanuatu" id="Vanuatu" frameborder="0" marginwidth="0" marginheight="0" allowfullscreen=""></iframe>
</div>
```
````

## Trade Estimation Methodologies

- General Methodology
  - Define port boundary
  - Generate port calls from boundary
  - Estimate trade / generate indicators
- <a href="https://www.imf.org/en/Publications/WP/Issues/2019/12/13/Big-Data-on-Vessel-Traffic-Nowcasting-Trade-Flows-in-Real-Time-48837"><b>2019 IMF: Big Data on Vessel Traffic: Nowcasting Trade Flows in Real Time</b><a>
  - Port Calls created by Marine Traffic
  - Data waterfall
    - Exclude: speed > 1.0 knot
    - Exclude: Anchorage and bunkering tankers - remove bunkering tankers
        - Fuel supplied to foreign vessels should be recorded as exports of the country according to international standards, although it is recognized that data collection may be challenging.6 Since the inclusion of these tankers introduces considerable volatility to the indices, we omit bunkering tankers from our valid port calls
    - Exclude: Ship arrived but not departerd
    - Exclude: Stay in the harbor outside reasonable range for trade activity
        - stay in port < 5hrs: unlikely to have enough time to load or unload goods in the port
        - stay in port > 60 hrs: Longer stays may be associated with ships visiting the port for repairs or maintenance services.
  - Indicators:
    - cargo number
        - cargo load
            - $ CWI_t = \sum_{i}^{} DWT_{i, t} \frac{|d_{i,t}^{D} - d_{i,t}^{A}|}{max(d_{i})} $
            - DWT is adjusted with a capacity utilization ratio.

- <a href="https://www.sciencedirect.com/science/article/pii/S1361920920305800"><b> 2020 Science Direct: Port disruptions due to natural disasters: Insights into port and logistics resilience</b><a>
  - no mention of how port calls were derived
  - ![image.png](ais/port-disruptions.png)

- <a href="https://www.imf.org/en/Publications/WP/Issues/2020/05/14/World-Seaborne-Trade-in-Real-Time-A-Proof-of-Concept-for-Building-AIS-based-Nowcasts-from-49393"><b> 2020 IMF: World Seaborne Trade in Real Time</b><a>
  - Port boundary:
    - SOG < 0.5, \& nav status anchored or moored

- <a href="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248818#pone.0248818.s001"><b> 2021 Global economic impacts of COVID-19 lockdown measures stand out in high-frequency shipping data</b><a>
  - Port Boundary: manually mapped, berthing + navigation channels
  - Port Calls: Vessel call algorithm
    - Filter:
      - include: cargo and tanker vessels.
      - exclude: stay in port less than 5h and more than the 95th percentile (of the port) are truncated, as they are most likely associated with refueling, repair or maintenance.
      - exclude: turnaround time of less than 10h and leave the port area at a direction that is within 45 degree of the direction of entering the port area. These port calls are most likely associated with vessels passing a port (e.g. ports alongside a river).

- <a href="https://www.imf.org/en/Publications/WP/Issues/2021/08/20/Tracking-Trade-from-Space-An-Application-to-Pacific-Island-Countries-464345"><b> 2021 IMF: Tracking Trade from Space: An Application to Pacific Island Countries</b><a>
  - Port Boundary: "manually determined using satellite imagery"
  - Port Call:
    - include: focus on container ships—the main engine of seaborne trade in the Pacific—vehicle carriers, and bulk carriers (relevant for Fiji, Nauru, and Solomon Islands as commodity-exporters).
    - exclude: Fuel tankers are not included, as Pacific countries import a significant portion of fuel for re-exports (for visiting foreign vessels and airlines
    - exclude vessels in transit: turnaround time of less than 5 hours and no draft change between the current and next port

## Additional Resources

- [AIS Handbook, Global Working Group on Big Data for Official Statistics](https://unstats.un.org/wiki/display/AIS/Introduction)
    > Data for this analysis is available through the UN Global Platform, which also
    hosts a dedicated working group to promote the use of AIS data to derive economic
    indicators.
