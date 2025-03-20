# Economic Analysis with News Sources

New analytical techniques have increased the role of non-traditional data sources for economic analysis, including text-based data. This research explores the use of text-based data from news articles, using natural language processing (NLP), to fill key data gaps on economic sentiments and prices, offering insights into relevant economic trends across the Pacific region.

## Data Sources

The Pacific region hosts a substantial corpus of accessible English-based content from newspapers and international news platforms, providing an opportunity to generate timely, comprehensive indicators of economic and political trends. Specifically, local news outlets from Pacific Island Countries (PICs), complemented by regional sources such as the Pacific Islands News Association (PINA), ABC Australia (ABC AU), and Radio New Zealand (RNZ), were selected due to their robust coverage and reliability. We used web-scraping techniques to extract articles from the selected sources, before organizing the contents into structured datasets.

**Table 1: News Sources by Country**

| Country         | Newspaper/Media Source                       | Number of Articles | From       |
|----------------|---------------------------------------------|--------------------|------------|
| Fiji          | Fiji Sun                                    | 46,350            | 2008-05-27 |
| Pacific       | Pacific Islands News Association (PINA)    | 26,151            | 2011-11-19 |
|               | Australian Broadcasting Corporation (ABC AU) | 16,297            | 2003-02-19 |
|               | Radio New Zealand (RNZ)                    | 18,160            | 2015-02-18 |
| Papua New Guinea | Post Courier                             | 6,278             | 2016-04-08 |
|               | PNG Business News                          | 2,197             | 2019-05-24 |
| Samoa        | Samoa Observer                             | 35,489            | 2012-01-01 |
| Solomon Islands | Solomon Islands Broadcasting Corporation (SIBC) | 9,062     | 2013-12-04 |
|               | Solomon Times                              | 11,139            | 2007-04-14 |
|               | Solomon Star                              | 14,484            | 2014-04-10 |
|               | The Island Sun                            | 9,117             | 2017-09-01 |
| Tonga        | Matangi Tonga Online                       | 14,071            | N/A        |
| Vanuatu      | The Daily Post                             | 29,469            | 2014-04-08 |
|               | Vanuatu Business Review                   | 577               | 2020-04-27 |
| **Total**    |                                           | **238,941**        |      |

## Methods

### Economic Policy Uncertainty Index (EPU) Index

One of the most influential applications of exploiting text data in economics is the Economic Policy Uncertainty (EPU) index first developed by {cite:t}`baker2016measuring`. In the initial application, an index of policy uncertainty was constructed based on analyzing the frequency of keywords related to economics, policy, and uncertainty in news articles. The authors found periods of elevated policy uncertainty to be strongly associated with declining in investment and employment, highlighting the negative impact of uncertainty on economic decision-making.

The construction of the EPU index follows a systematic approach where a news article must meet three criteria by containing at least one keyword from economic, policy, and uncertainty categories. Once the relevant news articles are identified, the EPU index is constructed through the following steps:

**Table 2: EPU Index Keywords**

| Category      | Words |
| ----------- | ----------- |
| Economic     | "economy", "economic", "economics", "business", "finance", "financial"       |
| Policy   |     "government", "governmental", "authorities", "minister", "ministry","parliament", "parliamentary", "tax", "regulation", "legislation", "central bank", "imf", "international monetary fund",  "world bank" |
| Uncertainty |     "uncertain", "uncertainty", "uncertainties", "unknown", "unstable" "unsure", "undetermined", "risky", "risk", "not certain", "non-reliable", "fluctuations", "unpredictable" |

- Let $ X_{it} = \frac{\text{EPU news in newspaper } i \text{ at time } t}{\text{All scraped news in newspaper } i \text{ at time } t} $ and pre-defined $T_1$ to be the standardization and normalization period.
- Calculate the standard deviation $\sigma_i$ for each newspaper $i$ over $T_1$.
- Standardize $X_{it}$ by dividing by $\sigma_i$ for all time $t$, resulting in $ Y_{it} = \frac{X_{it}}{\sigma_i} $
- Compute the mean of $Y_{it}$ over all newspapers in each month to obtain $ Z_t = \text{mean}(Y_{it}) \text{ at } t $
- Compute $M$, the mean value of $Z_t$ over the period $T_1$
- Normalize the EPU index by multiplying $Z_t$ by $ \left( \frac{100}{M} \right) $ for $T_1$, resulting in the normalized EPU time-series index with a mean of 100 over $T_1$.

<div class="flourish-embed flourish-chart" data-src="visualisation/22204379?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22204379/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

### Topic-based EPU

The EPU index can also be computed for news sources related to specific policy topics. To qualify, articles need to contain at least one keyword in each of the four criteria, namely (1) Economy, (2) Uncertainty, (3) Policy, and (4) Policy Topic - a list of terms for a specific theme (labor, inflation, climate, food security). Because the sample of articles that meet this refined criteria decreases, a topic-based EPU is constructed at the quarterly time frequency. The graphs below display quarterly EPU for jobs and inflation.

<div class="flourish-embed flourish-chart" data-src="visualisation/22205009?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22205009/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

### Economic Policy Sentiment

We use the EPU to filter news articles that align with the economic and policy categories for targeted sentiment analysis. The sentiment analysis uses VADER (Valence Aware Dictionary and sEntiment Reasoner), a rule-based model that handles social media and news text (Hutto and Gilbert, 2014). VADER calculates the sentiment score S based on the sum of lexical features (positive, neutral, and negative words). The final sentiment score S ranges between -1 (most negative) and +1 (most positive), with neutral scores around 0.

<div class="flourish-embed flourish-chart" data-src="visualisation/22205348?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22205348/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

### CPI and Inflation

Once we have obtained the EPU index for each country and period, we use the result as an input to analyze and predict price movements. To do so, we apply a three-month moving average (MA3) to smooth the volatile directly measured inflation data and introduce an additional policy category (using the same index approach described above) that focuses on inflation-specific terms. Finally, we conduct a regression analysis using variables selected through the cross-validated LASSO method.

## Results

### Country-Specific Models

At the country level, Fiji achieves the lowest RMSE at 0.739, indicating that the model’s predictions deviate by approximately 0.76 percentage points from the actual inflation values. Although Samoa and the Solomon Islands fail to accurately capture the magnitude of inflation, they exhibit stronger directional accuracy, correctly identifying inflationary and deflationary trends in the model evaluation with accuracies of 63.6 percent and 68.5 percent, respectively. Inflation volatility and the rapid alternation between deflation and inflation in PICs reduce prediction accuracy. Smoothing techniques considerably enhance the performance of the pooled model compared to country-specific approaches.

<div class="flourish-embed flourish-chart" data-src="visualisation/22209056?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22209056/thumbnail" width="100%" alt="chart visualization" /></noscript></div>

### Pooled Model

The pooled model using MA3 performs better than any of the country-level models with an accuracy of approximately 70 percent of the time and deviation around 0.70 percentage points from the actual inflation. This means that, based on historical data and the constructed EPU indexes, the models correctly predicted inflationary or deflationary trends more than two-thirds of the time.

<div class="flourish-embed flourish-chart" data-src="visualisation/22209247?2274258"><script src="https://public.flourish.studio/resources/embed.js"></script><noscript><img src="https://public.flourish.studio/visualisation/22209247/thumbnail" width="100%" alt="chart visualization" /></noscript></div>