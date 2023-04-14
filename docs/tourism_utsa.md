# Univaraite Time Series Analysis
## Empirical Modelling

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

To evaluate the model's performance, benchmark results will be provided.[^1] Three benchmark methods are employed:

- Average method, where the forecasts of all future values are equal to the average (or “mean”) of the historical data.
- Naïve method, setting all forecasts to be the value of the last observation.
- Drift method, $\hat{y}_{T+h|T} = y_{T} + \frac{h}{T-1}\sum_{t=2}^T (y_{t}-y_{t-1}) = y_{T} + h \left( \frac{y_{T} -y_{1}}{T-1}\right).$, which is equivalent to drawing a line between the first and last observations, and extrapolating it into the future.

[^1]: Rob J Hyndman and George Athanasopoulos, Forecasting: principles and practice (OTexts, 2018). See more [here](https://otexts.com/fpp3/simple-methods.html).