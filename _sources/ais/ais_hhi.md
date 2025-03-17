# Market concentration of vessel operators
Market concentration among vessel operators in Pacific Island countries can be analyzed using the Herfindahl-Hirschman Index (HHI):
$$
HHI =  \sum s_i^2 
$$

Where $s_i$ is the  market share of operator $i$. HHI value close to 0 indicates near perfect competition, while HHI value close to 1 indicates monopoly. 

Here, the market share is defined by the share of port calls from an operator. We use the [port calls data](ais_trade.md) derived from AIS, and the operator information from ship register data. Note that this excludes all vessels not registered with the IMO which is ~12% of port calls from cargo, tanker, and passenger vessels. 

## HHI ranked by country/vessel category 2024

The following graph displays the latest HHI values for each country and vessel category in 2024. The countries are ranked from highest (most concentrated) to lowest (most competitive) HHI.

<div class="flourish-embed flourish-scatter" data-src="visualisation/22163650?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22163650/thumbnail" width="100%" alt="scatter visualization" /></noscript></div>

## Change in HHI by country/vessel category, 2009 to 2024

This second graph shows the changes in HHI values for each country and vessel category from 2009 to 2024.

<div class="flourish-embed flourish-scatter" data-src="visualisation/22102411?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22102411/thumbnail" width="100%" alt="scatter visualization" /></noscript></div>