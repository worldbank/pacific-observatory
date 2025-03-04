# Market concentration of vessel operators
Market concentration among vessel operators in Pacific Island countries can be analyzed using the Herfindahl-Hirschman Index (HHI):
$$
HHI =  \sum s_i^2 
$$

Where $s_i$ is the  market share of operator $i$. HHI value close to 0 indicates near perfect competition, while HHI value close to 1 indicates monopoly. 

Here, the market share is defined by the share of port calls from an operator. We use the [port calls data](ais_trade.md) derived from AIS, and the operator information from ship register data. Note that this excludes all vessels not registered with the IMO which is ~12% of port calls from cargo, tanker, and passenger vessels. 

## Yearly HHI Per Country per Vessel Category 

% suggest 1 graph per vessel category (cargo, tanker, passenger)