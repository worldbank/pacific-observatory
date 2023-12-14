import numpy as np


class ScaledLogitScaler:
    """
    ScaledLogitScalar for multidimensional transformation using scaled logit transformation.

    Attributes:
    upper_ : numpy.ndarray
        Upper bounds calculated during fitting.
    lower_ : numpy.ndarray
        Lower bounds calculated during fitting.
    """

    def __init__(self, copy=True):
        self.copy = copy
    
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

    def inverse_transform(self, trans_X):
        """
        Applies inverse scaled logit transformation to the input data.

        Parameters:
        trans_X : numpy.ndarray
            Transformed array to be inverse-transformed.

        Returns:
        numpy.ndarray
            Inverse-transformed array.
        """
        return self._inverse_scaledlogit(trans_X, self.upper_, self.lower_)
