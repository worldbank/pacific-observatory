import numpy as np
import pandas as pd


def naive_method(y: pd.Series) -> pd.Series:
    """
    Calculates forecasts using the naive method for time series data.
    \hat{y}_{t+h} = y_{t}

    """
    forecast = y.shift(1)
    return forecast

def seasonal_naive_method(y: pd.array, period: int = 12) -> np.array:
    """
    Calculates forecasts using the seasonal naive method for time series data.

    Args:
        y (pd.array): A numpy array of time series data.
        period (int): The seasonal period of the time series, default to be 12.
    """
    n = len(y)
    forecasts = np.zeros(n)

    for i in range(period, n):
        forecasts[i] = y[i - period]

    return forecasts

def mean_method(y: np.ndarray) -> np.ndarray:
    """
    Calculates forecasts using the mean method for time series data.
    """
    n = len(y)
    mean = y.mean()
    forecasts = np.full(n, mean)

    return forecasts


def drift_method(y: np.ndarray, h: int) -> np.ndarray:
    """
    Calculates forecasts using the drift method for time series data.
    {y}_{T+h|T} = y_{T} + \frac{h}{T-1}\sum_{t=2}^T (y_{t}-y_{t-1}) = y_{T} + h \frac{y_{T} -y_{1}}{T-1}.

    Args:
        y (np.ndarray): A numpy array of time series data.
        h (int): The number of time periods to forecast into the future.
    """
    n: int = len(y)
    t: np.ndarray = np.arange(1, n+1)
    slope: float = (y[-1] - y[0]) / (n - 1)
    intercept: float = y[0] - slope
    forecasts: np.ndarray = slope * (t + h) + intercept

    return forecasts[-h:]

def calculate_evaluation(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Calculates the Root Mean Squared Error (RMSE) for time series data.

    Args:
        y_true (np.ndarray): A numpy array of the true values.
        y_pred (np.ndarray): A numpy array of the predicted values.

    Returns:
        dict: A dictionary containing the four performance metrics.
    """
    mse = np.mean((y_pred - y_true) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    y_true[y_true == 0] = 1e-10
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return  {'MSE': mse, 'RMSE': rmse, 'MAE': mae, 'MAPE': mape}
