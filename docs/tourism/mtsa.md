# Multivariate Time Series Analaysis
## Vector AutoRegressive (VAR)

Classical VAR would improve the univariate time series modeling by considering the linkages between ISA data from the GAD and the official VA data. A VAR(p) model is formally expressed as:

$$
VA_{t} = c + \alpha_{11}VA_{t-1} + \cdots + \alpha_{1p}VA_{t-p} 
+ \beta_{11}SAI_{t-1} + \cdots + \beta_{1p}SAI_{t-p} + Covid_{t} + \varepsilon_{t} 
$$

where $VA_t$ is the visitor arrivals by the official statistics at time $t$, $SAI_t$ is the international seat arrivals at time $t$, and $Covid_t$ is a dummy variable to be one after the WHO announced Covid-19 as the global pandemic. Each equation is estimated via Ordinary Least Squares (OLS). The standard approach for the selection of order p is the Akaike information criterion (AIC).

Impulse Response Analysis (IRA), which describes the evolution of a model’s variables in reaction to a shock in one or more variables, would also be employed to examine how ISA's changes would affect VA. To further check the model's robustness, pairwise Granger causality tests after VAR and the autocorrelation check of the residuals would be employed.
