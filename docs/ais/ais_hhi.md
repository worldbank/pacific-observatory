# Market concentration of vessel operators
Market concentration among vessel operators in Pacific Island countries can be analyzed using the Herfindahl-Hirschman Index (HHI):

```{math}
HHI = \sum s_i^2
```

Where $s_i$ is the  market share of operator $i$. HHI value close to 0 indicates near perfect competition, while HHI value close to 1 indicates monopoly. 

Here, the market share is defined by the share of port calls from an operator. We use the [port calls data](ais_trade.md) derived from AIS, and the operator information from ship register data. Note that this excludes all vessels not registered with the IMO which is ~12% of port calls from cargo, tanker, and passenger vessels. 

The following interactive graph displays yearly HHI values for each country by vessel category. To use this graph:

1. **Compare two years**: Select different years in both fields to see how market concentration changed between them.
2. **View a single year**: Select the same year in both fields to see a snapshot of that year's data.
3. **Change vessel category**: Use the category selector to view HHI values for different vessel types.

Note: Countries are sorted according to the latest year selected.

<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <iframe src="../interactive/ais/hhi-compare.html"
          frameborder="0"
          scrolling="no"
          style="width: 100%; height: 660px;">
  </iframe>
</div>


