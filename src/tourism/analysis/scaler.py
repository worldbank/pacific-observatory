"""
The module provides time seris transformation methods (Scaled Logit and Differencing).

Dependencies:
    numpy (np)
    pandas (pd)

Last Modified:
    2024-02-01
"""
from typing import Optional
import numpy as np
import pandas as pd

class ScaledLogitScaler:
    """
    ScaledLogitScalar for transformation using scaled logit transformation.

    Attributes:
    upper_ : numpy.ndarray
        Upper bounds calculated during fitting.
    lower_ : numpy.ndarray
        Lower bounds calculated during fitting.
    """

    def __init__(self, copy=True):
        self.copy = copy
        self.upper_ = None
        self.lower_ = None
        self.data_range_ = None

    def _scaledlogit_transform(self, series):
        """
        Applies scaled logit transformation to the input series.

        Parameters:
        series : numpy.ndarray
            Input array to be transformed.

        Returns:
        numpy.ndarray
            Transformed array using scaled logit.
        """
        upper = np.nanmax(series, axis=0) + 1
        lower = np.nanmin(series, axis=0) - 1
        scaled_logit = np.log((series - lower) / (upper - series))
        return scaled_logit

    def _inverse_scaledlogit(self, trans_series, upper, lower):
        """
        Applies inverse scaled logit transformation to the input series.

        Parameters:
        trans_series : numpy.ndarray
            Transformed array to be inverse-transformed.
        upper : numpy.ndarray
            Upper bounds used in the transformation.
        lower : numpy.ndarray
            Lower bounds used in the transformation.

        Returns:
        numpy.ndarray
            Inverse-transformed array.
        """
        exp = np.exp(trans_series)
        inv_series = (((upper - lower) * exp) / (1 + exp)) + lower
        return inv_series

    def _reset(self):
        if hasattr(self, "upper_"):
            del self.upper_
            del self.lower_
            del self.data_range_


    def fit(self, X):
        """ 
        Fits the scaler to the input data by calculating upper and lower bounds.

        Parameters:
        X : numpy.ndarray
            Input data to fit the scaler.
        """
        # Reset internal state before fitting
        self._reset()
        self.upper_ = np.nanmax(X, axis=0) + 1
        self.lower_ = np.nanmin(X, axis=0) - 1
        self.data_range_ = self.upper_ - self.lower_
        return self

    def transform(self, X):
        """
        Applies scaled logit transformation to the input data.

        Parameters:
        X : numpy.ndarray
            Input data to be transformed.

        Returns:
        numpy.ndarray
            Transformed array using scaled logit.
        """
        return self._scaledlogit_transform(X)

    def inverse_transform(self, transformed):
        """
        Applies inverse scaled logit transformation to the input data.

        Args:
            transformed: Transformed array to be inverse-transformed.

        Returns:
            Inverse-transformed array.
        """
        return self._inverse_scaledlogit(transformed, self.upper_, self.lower_)


class Differencing:
    """
    A class for performing differencing operations on time series data.

    Attributes:
        initial_value (Optional[float]): The first value of the original time series, 
            stored during transformation.
    """
    def __init__(self):
        self.initial_value: Optional[float] = None

    def transform(self, series: pd.Series):
        """
        Transforms the original time series to its differenced version.

        Args:
            series (pd.Series): The original time series data.

        Returns:
            differenced (pd.Series): The differenced series with the first value dropped.
        """
        self.initial_value = series.iloc[0]
        differenced = series.diff().dropna()
        return differenced

    def inverse_transform(self,
                          differenced: pd.Series,
                          temporary:Optional[float]=None):
        """
        Reverts the differenced series back to its original form.

        Args:
            differenced (pd.Series): The differenced time series data.
            temporary (Optional[float]): An optional temporary initial value to use 
                for the inversion process. If None, the stored initial value from 
                the transform method is used.

        Returns:
            original (pd.DataFrame): The original time series data before differencing.
        """
        # Adding the initial value back to the first element of the differenced series
        if temporary is not None:
            original = pd.DataFrame(differenced).cumsum() + temporary
        else:
            original = pd.DataFrame(differenced).cumsum() + self.initial_value
        return original
