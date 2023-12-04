import numpy as np


class ScaledLogitScalar:
    """
    ScaledLogitScalar for multidimensional transformation using scaled logit transformation.

    Attributes:
    upper_ : numpy.ndarray
        Upper bounds calculated during fitting.
    lower_ : numpy.ndarray
        Lower bounds calculated during fitting.
    """

    @staticmethod
    def scaledlogit_transform(series):
        """
        Applies scaled logit transformation to the input series.

        Parameters:
        series : numpy.ndarray
            Input array to be transformed.

        Returns:
        numpy.ndarray
            Transformed array using scaled logit.
        """
        upper = series.max(axis=0) + 1
        lower = series.min(axis=0) - 1
        scaled_logit = np.log((series - lower) / (upper - series))
        return scaled_logit

    @staticmethod
    def inverse_scaledlogit(trans_series, upper, lower):
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

    def fit(self, X):
        """
        Fits the scaler to the input data by calculating upper and lower bounds.

        Parameters:
        X : numpy.ndarray
            Input data to fit the scaler.
        """
        self.upper_ = X.max(axis=0) + 1
        self.lower_ = X.min(axis=0) - 1

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
        return self.scaledlogit_transform(X)

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
        return self.inverse_scaledlogit(trans_X, self.upper_, self.lower_)
