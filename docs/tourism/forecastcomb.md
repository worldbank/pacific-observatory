# Forecast Combination
In this study, several combination methods are used to test the performance of the different forecasting models.

## Linear Combination Weights
Consistent with [Stock and Waston (1998)](https://www.nber.org/system/files/working_papers/w6607/w6607.pdf)'s experiment on linear combination weights, the combined forecasts are the weighted averages of the single forecasts. Let $MSE_{t+h,t,i} = (1/v)\sum_{\tau=t-v}^{t} e^{2}_{\tau,\tau−h,i}$ be the $i$th forecasting model’s MSE at time $t$, computed over a window of the previous $v$ periods. Then 

$$
    \hat{y}_{t+h,t} = \sum_{i=1}^{N} \hat{\omega}_{t+h,t,i} \hat{y}_{t+h,t,i}, \text{ where } \hat{\omega}_{t+h,t,i} = \frac{(1/MSE_{t+h,t,i}^{\kappa})}{\sum_{j=1}^{N} (1/MSE_{t+h,t,j}^{\kappa})}
$$

When $\kappa = 0$, $MSE_{t+h,t,i}^{\kappa}$ would be $1$, and the weight is assigned equally to every single forecast, suggesting the arithmetic average of forecasts. As $\kappa$ increases, an increasing amount of weight is assigned to models that perform well, and the weight is equal to the inverse of MSE when $\kappa = 1$. The study tests two specific scenarios where $\kappa = 0$ and $\kappa = 1$.

## Least squares estimators of the weights
Least square estimators of the weights are computed by the ordinary least squares, regressing realizations of the target variable $y_{\tau}$ the N-vector of forecasts, $\hat{y}_{\tau}$  using data over the period $\tau = h, . . . , t$:

$$
\hat{\omega}_{t+h,t} = (\sum_{\tau=1}^{t-h} \hat{y}_{\tau+h,\tau} \hat{y}_{\tau+h,\tau}')^{-1} \sum_{\tau=1}^{t-h} \hat{y}_{\tau+h,\tau} y_{\tau+h}
$$ 