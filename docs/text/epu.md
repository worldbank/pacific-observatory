# Economic Policy Uncertainty Index (EPU)

Uncertainty poses challenges to the stability and growth of economies. The Economic Policy Uncertainty Index (EPU) developed by {cite:t}`baker2016measuring` emerges as a vital tool to measure both economic- and policy-related uncertainties. Sepcifically, a news needs to contain at least one keyword in each of the three criteria, namely (1) Economy, (2) Uncertainty, and (3) Policy. After counting the frequency of EPU news (in relative to all news), the EPU index can be produced by following steps:

| Category      | Words |
| ----------- | ----------- |
| Economic     | "economy", "economic", "economics", "business", "finance", "finianal"       |
| Policy   |     "government", "governmental", "authorities", "minister", "ministry","parliament", "parliamentary", "tax", "regulation", "legislation", "central bank", "imf", "international monetary fund",  "world bank" |
| Uncertainty |     "uncertain", "uncertainty", "uncertainties", "unknown", "unstable" "unsure", "undetermined", "risky", "risk", "not certain", "non-reliable", "fluctuations", "unpredictable" |

- Let $ X_{it} = \frac{\text{EPU news in newspaper } i \text{ at time } t}{\text{All scraped news in newspaper } i \text{ at time } t} $ and pre-defined $T_1$ to be the standardization and normalization period;

- Calculate the standard deviation $\sigma_i$ for each newspaper $i$ over $T_1$.

- Standardize $X_{it}$ by dividing by $\sigma_i$ for all time $t$, resulting in $ Y_{it} = \frac{X_{it}}{\sigma_i} $

- Compute the mean of $Y_{it}$ over all newspapers in each month to obtain $ Z_t = \text{mean}(Y_{it}) \text{ at } t $

- Compute $M$, the mean value of $Z_t$ over the period $T_1$

- Normalize the EPU index by multiplying $Z_t$ by $ \left( \frac{100}{M} \right) $ for $T_1$, resulting in the normalized EPU time-series index with a mean of 100 over $T_1$.

Beyond the $Z_t$ being arithmetic mean of $Y_{it}$, we develop a weighted scheme where $w_{it} = \frac{\text{news in newspaper }i \text{ at time }t}{\text{All scraped news at time } t}$ and $Z_t = \sum_{i=1}^{n} w_{it} Y_{it} $ for $n$ newspapers. The very rationale behind is to overcome the scenario where a single newspaper with a small number of both news and EPU news creates voltaility for the EPU index. The weighted EPU index is displayed as below with 2016 to 2021 being the standardization and normalization period, as represented by green dashed line.

<div>
<iframe src="https://worldbank.github.io/pacific-observatory/interactive/text/epu_pic.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="750"></iframe>
</div>

## Economic Policy Sentiment

The sentiment of economic policy-related news could act as a barometer for uncertainty. Analyzing the shifts and changes in the sentiment of news articles and reports pertaining to economic policy could reflect the underlying economic uncertainty. To construct the sentiment scores, we firstly filters news identified as "economic" and "policy," calculates the sentiment (polarity) score for each news, and aggregates scores by each month.

<div>
<iframe src="https://worldbank.github.io/pacific-observatory/interactive/text/ep_sentiment.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="750"></iframe>
</div>

## EPU Indexes for Policy Categories

EPU for policy categories provide a more granular approach to delve into the interested policy category. To qualify, we search for articles which contain at least one keyword in each of the four criteria, namely (1) Economy, (2) Uncertainty, and (3) Policy and a list of terms for Sepcific Policy category.

For example, the below graph displays the EPU index related to job with a list of job-related words.

<div>
<iframe src="https://worldbank.github.io/pacific-observatory/interactive/text/epu_pic_job.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="750"></iframe>
</div>