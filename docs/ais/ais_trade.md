# Port Arrivals and Trade Volume

This page presents AIS-derived port-level statistics for the Pacific Islands. Motivated by the work of {cite:t}`Arslanalp2021`, our initial study focus on port arrivals and trade volume estimates for Samoa {cite:p}`WBAIS-Samoa`, and to the rest of the pacific countries {cite:p}`WBAIS-Pacific`. We find that our derived port calls data accurately capture international trade-related ships, and whilst cargo volume levels are off from official data, they can still capture variation when pooled together. Here, we present an updated version of these statistics, incorporating AIS data from as early as 2011 providing a longitudinal dataset for further study.

## Data and Methods
The datasets used are hourly AIS data within the pacific region from 2011-2024 provided by S&P, ship register data from the UNGP, port boundaries from {cite:t}`Arslanalp2021`. The countries covered are Fiji, Kiribati, Marshall Islands, Micronesia, Nauru, Palau, Papua New Guinea, Samoa, Solomon Islands, Tonga, Tuvalu, and Vanuatu. We followed the movement aggregation method from the {cite:t}`ADB2023` to capture the port arrivals making use of their helper functions available in the `ais` python package.    

For trade volume estimation, we follow the methods from {cite:t}`Arslanalp2021` which is based on the volume displacement of the ship. To get the volume of the cargo, the vessel's displacement upon arrival and departure are estimated using the formula:

$$
Disp_d = L \times W \times d \times \rho \times c_d 
$$ (dispeq)

Where $Disp_d$ is the vessel displacement given length $L$, width $W$, reported draft $d$, density of salt water $\rho$ and block coefficient at reported draught $c_d$. To get $c_d$, the block coeffient at maximum levels, called *design* block coefficient $c_D$ is required. Here, we introduce a derivation of $c_D$ from {eq}`dispeq` by using maximum draught $D$ and maximum displacement $Disp_D$ which are availabe in the ship register data: 

$$
c_D = \frac{Disp_D}{L \times W \times D \times \rho } 
$$ (cdesign)

We get the difference between the departure and arrival displacements to get the estimate of volume of cargo loaded/unloaded. If the net displacement is positive, it is assumed that the cargo for exports, and for imports otherwise. 

## Port Arrivals 

<div class="custom-embed port-calls-chart">
  <iframe
    src="interactive/ais/port%20calls.html"
    style="border: 0; width: 100%; height: 600px;"
    title="Port Calls Dashboard"
    allowfullscreen>
  </iframe>
  <noscript>
    <p><a href="interactive/ais/port%20calls.html">View the dashboard</a></p>
  </noscript>
</div>



## Trade Volume

<div class="flourish-embed flourish-chart" data-src="visualisation/19837444?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/19837444/thumbnail" width="100%" alt="chart visualization" /></noscript></div>


## Data Availability

The output data from this analysis is publicly available through the [Development Data Catalog](https://datacatalog.worldbank.org/search/dataset/0062856/Pacific%20Observatory%20Datasets?version=6).

## References

```{bibliography}
:filter: docname in docnames
```