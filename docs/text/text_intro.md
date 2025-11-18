# Economic Analysis with News Sources

New analytical techniques have increased the role of non-traditional data sources for economic analysis, including text-based data. This research explores the use of text-based data from news articles, using natural language processing (NLP), to fill key data gaps on economic sentiments and prices, offering insights into relevant economic trends across the East Asia and Pacific region.

## Data Sources

The East Asia and Pacific region hosts a substantial corpus of accessible English-based content from newspapers and international news platforms, providing an opportunity to generate timely, comprehensive indicators of economic and political trends. Specifically, local news outlets from East Asia and Pacific countries, complemented by regional sources such as the Pacific Islands News Association (PINA), ABC Australia (ABC AU), and Radio New Zealand (RNZ), were selected due to their robust coverage and reliability. We used web-scraping techniques to extract articles from the selected sources, before organizing the contents into structured datasets.

**Table 1: News Sources by Country**

| Country | Newspaper/Media Source | Number of Articles | From |
|---------|------------------------|--------------------|----|
| Cambodia | Khmer Times | 51,791 | 1970-01-01 |
| China | China Daily | 10,446 | 2014-03-28 |
| | People's Daily Online | 3,155 | 2024-09-13 |
| Fiji | Fiji Sun | 18,348 | 2010-03-09 |
| Indonesia | Antara | 10,702 | 2025-09-23 |
| | Jakarta Post | 1,601 | 2025-02-24 |
| | Tempo | 77,615 | 2003-07-21 |
| Japan | Japan News | 50,189 | 2022-04-29 |
| | Japan Today | 4,500 | 2012-09-27 |
| | The Asahi Shimbun | 11,206 | 2020-04-16 |
| Lao | The Laotian Times | 8,645 | 2016-06-03 |
| Malaysia | Malay Mail | 223,714 | 2013-06-18 |
| Marshall Islands | MI Journal | 1,605 | 2015-01-02 |
| Mongolia | UB Post | 456 | 2016-10-08 |
| New Zealand | New Zealand Herald | 16,482 | 2025-06-10 |
| Pacific | Australian Broadcasting Corporation (ABC AU) | 25,418 | 2003-02-19 |
| | PINA | 33,597 | 2011-11-19 |
| | Radio New Zealand (RNZ) | 52,666 | 2007-06-17 |
| Palau | Island Times | 10,019 | 2016-06-03 |
| Papua New Guinea | PNG Business News | 3,434 | 2019-05-24 |
| | Post Courier | 52,679 | 2015-12-16 |
| Philippines | Asia News Network | 2,991 | 2018-04-03 |
| | Inquirer | 50,676 | 1998-10-07 |
| | Philippine Star | 220 | 2025-10-11 |
| Samoa | Samoa Observer | 77,432 | 2012-01-01 |
| Singapore | The Independent | 1,834 | 2022-10-17 |
| | The Straits Times | 9,779 | 2024-09-15 |
| | Today Online | 616 | 2024-04-13 |
| Solomon Islands | SIBC | 10,846 | 2013-12-14 |
| | Solomon Star | 34,109 | 2014-04-10 |
| | Solomon Times | 22,976 | 2007-04-14 |
| | The Island Sun | 10,296 | 2017-09-01 |
| South Korea | The Korea Herald | 9,424 | 2025-05-05 |
| | The Korea Times | 93,767 | 2006-12-07 |
| Thailand | Nation Thailand | 13,830 | 2024-04-22 |
| Tonga | Matangi Tonga Online | 40,383 | 1997-11-04 |
| Vanuatu | Vanuatu Daily Post | 34,927 | 2014-04-08 |
| | Vanuatu Business Review (VBR) | 577 | 2020-04-27 |
| Vietnam | Tuoi Tre | 36,464 | 1970-01-01 |
| **Total** | | **1,175,259** | |

## Methods

### Economic Policy Uncertainty (EPU) Index

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

<div>
<iframe src="../interactive/text/epu_pic.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="433"></iframe>
</div>

### Topic-based EPU

The EPU index can also be computed for news sources related to specific policy topics. To qualify, articles need to contain at least one keyword in each of the four criteria, namely (1) Economy, (2) Uncertainty, (3) Policy, and (4) Policy Topic - a list of terms for a specific theme (labor, inflation, climate, food security). Because the sample of articles that meet this refined criteria decreases, a topic-based EPU is constructed at the quarterly time frequency. The graphs below display quarterly EPU for jobs and inflation.

<div>
<iframe src="../interactive/text/epu_topics_pic.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="433"></iframe>
</div>

### Economic Policy Sentiment

We use the EPU to filter news articles that align with the economic and policy categories for targeted sentiment analysis. The sentiment analysis uses VADER (Valence Aware Dictionary and sEntiment Reasoner), a rule-based model that handles social media and news text (Hutto and Gilbert, 2014). VADER calculates the sentiment score S based on the sum of lexical features (positive, neutral, and negative words). The final sentiment score S ranges between -1 (most negative) and +1 (most positive), with neutral scores around 0.

<div>
<iframe src="../interactive/text/sentiment_pic.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="433"></iframe>
</div>

### Consumer Price Index (CPI) and Inflation

Once we have obtained the EPU index for each country and period, we use the result as an input to analyze and predict price movements. To do so, we obtain the [International Monetary Fund (IMF) Consumer Price Index (CPI) data](https://data.imf.org/en/datasets/IMF.STA:CPI) and apply a three-month moving average (MA3) to smooth the volatile directly measured inflation data. We introduce additional policy categories (using the same index approach described above) that focus on inflation- and job-specific terms. Finally, we conduct a regression analysis using variables selected through the cross-validated LASSO method.

## Results

### Country-Specific Models

We use a training set of seven countries to evaluate the performance of the country-specific models. These are China, Fiji, Indonesia, Japan, Lao, Samoa, Solomon Islands, and Tonga. At the country level, Japan achieves the lowest RMSE at 0.11, indicating that the model’s predictions deviate by approximately 0.11 percentage points from the actual inflation values. Countries with the highest accuracy are Lao, Indonesia, and Samoa, achieving accuracies of 0.95, 0.88, and 0.84, respectively. Inflation volatility and the rapid alternation between deflation and inflation amongst countries reduce prediction accuracy. 

<div>
<iframe src="../interactive/text/train_predictions_pic.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="433"></iframe>
</div>

### Pooled Model

The pooled model using MA3 achieves an accuracy of approximately 83.1 percent of the time and deviation around 0.83 percentage points from the actual inflation. This means that, based on historical data and the constructed EPU indexes, the models correctly predicted inflationary or deflationary trends more than four out of five times.

For out-of-sample validation of the pooled model, we use a set of three countries: Philippines, South Korea, and Vietnam. Philippines achieves a RMSE of 0.14 and an accuracy of 92.91%. South Korea achieves a RMSE of 0.15 and an accuracy of 84.25%, and Vietnam achieves a RMSE of 0.17 and an accuracy of 88.43%.

<div>
<iframe src="../interactive/text/out_of_bag_predictions_pic.html"
frameborder="0" marginwidth="0" marginheight="0" width="800" height="433"></iframe>
</div>

## Future Work

Future work will involve the development of a methodology that can interpolate quarterly CPI data to monthly values, bring lagged CPI data to the same time frequency as the EPU index, and generate inflation predictions on countries with no inflation data.

**Table 3: IMF CPI Data Availability by Country**


| Country Name     | ISO3   | Frequency   | Last Reported   |
|:-----------------|:-------|:------------|:----------------|
| American Samoa   | ASM    | No Data     | No Data         |
| Guam             | GUM    | No Data     | No Data         |
| Marshall Islands | MHL    | No Data     | No Data         |
| New Zealand      | NZL    | Quarterly   | 2025-Q3         |
| Palau            | PLW    | Quarterly   | 2025-Q2         |
| Papua New Guinea | PNG    | Quarterly   | 2025-Q2         |
| Thailand         | THA    | Monthly     | 2025-M03        |
| Tonga            | TON    | Monthly     | 2025-M01        |
| Tuvalu           | TUV    | Quarterly   | 2012-Q2         |
| Vanuatu          | VUT    | Quarterly   | 2023-Q4         |
| Vietnam          | VNM    | Monthly     | 2025-M03        |
