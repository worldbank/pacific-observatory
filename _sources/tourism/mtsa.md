# Multivariate Time Series Analaysis
## Vector AutoRegressive (VAR)

Classical VAR would improve the univariate time series modeling by considering the linkages between ISA data from the GAD and the official VA data. A VAR(p) model is formally expressed as:

$$
VA_{t} = c + \alpha_{11}VA_{t-1} + \cdots + \alpha_{1p}VA_{t-p} 
+ \beta_{11}SAI_{t-1} + \cdots + \beta_{1p}SAI_{t-p} + Covid_{t} + \varepsilon_{t} 
$$

where $VA_t$ is the visitor arrivals by the official statistics at time $t$, $SAI_t$ is the international seat arrivals at time $t$, and $Covid_t$ is a dummy variable to be one after the WHO announced Covid-19 as the global pandemic. Each equation is estimated via Ordinary Least Squares (OLS). The standard approach for the selection of order p is the Akaike information criterion (AIC).

Impulse Response Analysis (IRA), which describes the evolution of a model’s variables in reaction to a shock in one or more variables, would also be employed to examine how ISA's changes would affect VA. To further check the model's robustness, pairwise Granger causality tests after VAR and the autocorrelation check of the residuals would be employed.

## Ratio Approach [Temporarily]
Unlike the VAR that the vector contains multiple series, the alternative way to link the GAD with official VA data is to produce a single ratio by setting $VA_t$ as the numerator and $ISA_t$ as the denominator ($ratio_{t}=\frac{VA_t}{ISA_t}$). The produced ratio is similar to the load factor in aviation analysis, where $ \text{LF}=\frac{\text{Number of Carried Passengers} * \text{Distance}}{\text{Available Seats} * \text{Distance}}$. By assuming the distance is fixed for each passenger, the available seats equal to $ISA_t$ in our ratio formula, and we can treat $VA_t$ as a proxy of the number of carried passengers. Thus, we have the model:

$$ 
Ratio_t = TravelIndex_t + Quarter_t + Covid * StringencyIndex_t + NumofCruise_t + \varepsilon_{t} 
$$