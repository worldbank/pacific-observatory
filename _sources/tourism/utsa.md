# Individual forecasts

## SARIMAX

Built on the previous tourism research, a Seasonal Auto-Regressive Integrated Moving Average with eXogenous factors (SARIMAX) model would be employed to track each PIC's VAs. A SARIMAX model consists of three elements: AR, MA, and X. The AR part of the model use the past values of the differenced series to make predictions, while the MA part uses the past errors of the model. An SARIMAX $(p,d,q)(P,D,Q,s)$ is defined as below:

$$
\Theta(L)^{p} \theta(L^{s})^{P} \Delta^{d} \Delta_{s}^{D} VA_{t} = \Phi(L)^{q} \phi(L^{s})^{Q} \Delta^{d} \Delta_{s}^{D} \epsilon_{t} + \sum_{i=1}^{n} \beta_{i} {x}_{t}^{i}
$$

where: 

- ${VA}_{t}$ is the Visitor Arrivals at time $t$
- ${x}_{t}^{i}$ for $i <= n$ with coefficients $\beta_{i}$ denotes $n$ exogenous variables defined at each time step $t$
- $L$ is the lag operator and $L^{s}$ is the seasonal lag operator 
- $p$ is the order of the AR part, $q$ is the order of the MA part, and $d$ is the degree of first differencing involved
- $\Theta(L)^{p}$ is an order $p$ polynomial function of $L$ from the AR part, and $\phi$ is defined analogously to $\Theta$.
- $\Delta^{d}$ is the integration operator and $\Delta_{s}^{D}$ takes the seasonal differences of the series

The model employs the scaled logit transformation to avoid negative predictions, transforming $x$ to $\log(\frac{x-a}{b-x})$, where $a$ is the lower bound and $b$ is the upper bound. Further, to prevent -$\infty$, $a$ is set to be slightly smaller than the minimum of the series, and $b$ is slightly larger than the maximum.

## Vector AutoRegressive and Moving Average Model (VARMA)

Given the potential relationship between offical VA and GAD data, VARMA model COULD improve the univariate time series modeling by considering the linkages between ISA from the GAD and the official VA data. A VAR(p) model with exogenous variables is formally expressed as:

$$
VA_{t} = c + \alpha_{11}VA_{t-1} + \cdots + \alpha_{1p}VA_{t-p} 
+ \beta_{11}SAI_{t-1} + \cdots + \beta_{1p}SAI_{t-p} + Covid_{t} + TravelIndex_t + \varepsilon_{t} 
$$

where $VA_t$ is the visitor arrivals by the official statistics at time $t$, $SAI_t$ is the international seat arrivals at time $t$, and $Covid_t$ is a dummy variable to be one after the WHO announced Covid-19 as the global pandemic. Each equation is estimated via Ordinary Least Squares (OLS). The standard approach for the selection of order p is the Akaike information criterion (AIC).

## Ratio Approach

Unlike the VAR that the vector contains multiple series, the alternative way to link the GAD with official VA data is to produce a single ratio by setting $VA_t$ as the numerator and $ISA_t$ as the denominator ($ratio_{t}=\frac{VA_t}{ISA_t}$). The produced ratio is similar to the load factor in aviation analysis, where $ \text{LF}=\frac{\text{Number of Carried Passengers} * \text{Distance}}{\text{Available Seats} * \text{Distance}}$. By assuming the distance is fixed for each passenger, the available seats equal to $ISA_t$ in our ratio formula, and we can treat $VA_t$ as a proxy of the number of carried passengers.[^1] Thus, we have the model:

$$
Ratio_t = TravelIndex_t + Quarter_t + (Covid_t * StringencyIndex_t) + \varepsilon_{t} 
$$
where:

- $TrvalIndex_t$ is the Google Search Index data at time $t$;
- $Covid_t$ is a dummy variable set to be 1 after WHO announced the Covid-19 as global pandemic;
- $StringencyIndex_t$ from the [OWID Global Stringency Index](https://ourworldindata.org/covid-stringency-index);

The limited sample size (smaller than 48) and potential autocorrelation would violate the homoskedasticity assumption by OLS but still produce an unbiased estimation. Thus, to correct the standard error, we employ the Heteroskedasticity- and Autocorrelation- Consistent estimator (HAC) and choose the lag same as Wooldridge suggests where $h = [4(T/100)^{2/9}] + 1$.

## Model Evaluation

To evaluate the model's performance, benchmark results will be provided.[^2] Three benchmark methods are employed:

- Average method, where the forecasts of all future values are equal to the average (or “mean”) of the historical data.
- Naïve method, setting all forecasts to be the value of the last observation.
- Drift method, $\hat{y}_{T+h|T} = y_{T} + \frac{h}{T-1}\sum_{t=2}^T (y_{t}-y_{t-1}) = y_{T} + h \left( \frac{y_{T} -y_{1}}{T-1}\right).$, which is equivalent to drawing a line between the first and last observations, and extrapolating it into the future.

For each method, Mean Squared Error (MSE), Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and Symmetric Mean Absolute Percentage Error (SMAPE) are provided. [^3]

[^1]: A hideen assumption behind employing the ratio approach is the airline company would dynamically adjust the to choose the combination of fares, aircraft size, and load factor to maximize profits in each market. See more in [Graham, Kaplan, and Sibley (1983)](https://www.jstor.org/stable/3003541)
[^2]: Rob J Hyndman and George Athanasopoulos, Forecasting: principles and practice (OTexts, 2018). See more [here](https://otexts.com/fpp3/simple-methods.html).
[^3]: Mean Absolute Percentage Error (MAPE) is also a frequent calculation, but given there exists some zero values in the actual value, and the result would lead to $+\infty$ considering $MAPE(y, \hat{y})= \frac{100\%}{N} \sum_{i=0}^{N - 1} \frac{|y_i - \hat{y}_i|}{|y_i|}$.