"""
The module includes univariate time series analysis methods (SARIMAX, STL, 
    and Prophet) for visitor arrivals.

Last Modified:
    2024-02-02
"""
import os
from typing import Union, Dict
import pandas as pd
from tqdm import tqdm
#!pip install pmdarima
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from prophet import Prophet
from .scaler import ScaledLogitScaler
from .ts_eval import (naive_method, seasonal_naive_method,
                      mean_method, calculate_evaluation)
from .data import SARIMAXData
from .ts_utils import generate_search_params


__all__ = [
    "SARIMAXPipeline",
    "OtherTSToolKits"
]


class SARIMAXPipeline(SARIMAXData):
    """
    A SARIMAX Wrapper

    To use:
        model = SARIMAXPipeline(country="samoa",
                      training_ratio=1,
                      y_var="total",
                      exog_var=["covid", "stringency_index", "samoa_travel"],
                      transform_method="scaledlogit")
        model.read_and_merge()
        model.transform()
        model.stepwise_search()
        model = model.manual_search()
    """

    def __init__(self,
                 country: str,
                 y_var: str,
                 exog_var: list,
                 transform_method: str,
                 training_ratio=0.9,
                 verbose=True,
                 trends_data_folder: str = os.path.join(
                     os.getcwd(), "data", "tourism", "trends"),
                 covid_idx_path: str = os.path.join(os.getcwd(),
                                                    "data", "tourism",
                                                    "oceania_covid_stringency.csv")):
        """
        Initialize SARIMAXPipeline object.

        Args:
          y (str): The name of the column representing the time series variable.
          exog_var (list, optional): The list of the column names representing 
            the exogenous variable.
          transform_method (str, optional): The name of the transformation method 
            to apply to the time series.
          training_ratio (float, optional): The proportion of the data to use 
            for training the model.
          verbose (bool): Logging the model running or not.

        Raises:
            AttributeError: If an invalid transformation method is specified.
        """
        super().__init__(country, y_var, exog_var, trends_data_folder, covid_idx_path)
        if transform_method not in ["scaledlogit", "minmax", None]:
            raise AttributeError("No such transformation exists.")
        self.transform_method = transform_method
        self.y = None
        self.transformed_y = None
        self.exog = None
        self.total_size = None
        self.training_ratio = training_ratio
        self.test_size = None
        self.training_size = None
        self.verbose = verbose
        self.scaler = None
        self.benchmark = None
        self.stepwise_fit = None
        self.stepwise_model = None
        self.manual_search_results = None

    def transform(self):
        """
        Transforms the time series data based on specified transformation methods. 

        This method primarily handles the partitioning of data into training and testing sets 
        and applies a transformation to the dependent variable (y_var). The transformation 
        method is determined by the 'transform_method' attribute of the object. Currently, 
        it supports 'scaledlogit' and 'minmax' transformations.

        The method checks whether the training data includes the COVID-19 period 
        (after March 11, 2020). If not, it sets the training size to cover the entire dataset, 
        ensuring the model trains on the COVID-19 period.

        Args:
          y (pd.DataFrame): The dependent variable extracted from the data.
          exog (pd.DataFrame): The exogenous variables extracted from the data.
          total_size (int): The total number of observations in the data.
          training_size (int): The number of observations in the training set.
          test_size (int): The number of observations in the test set.
          transformed_y (pd.DataFrame): The transformed dependent variable.

        Prints:
          The sizes of the training and testing datasets.
          A message if the training data does not cover the COVID-19 period.

        Raises:
            ValueError: If an unknown transformation method is specified.
        """

        # Load the data
        self.y = self.data[[self.y_var]]
        self.exog = self.data[self.exog_var]
        self.total_size = len(self.data)
        self.training_size = int(self.training_ratio * self.total_size)
        self.test_size = self.total_size - self.training_size

        if self.data["date"][self.training_size-1] <= pd.Timestamp(2020, 3, 11):
            print(
                "Training samples do not cover covid-19 periods. Instead, Run All Samples.")
            self.training_size = self.total_size
            self.test_size = 0

        print(
            f"training size : {self.training_size}, testing size : {self.test_size}")

        if self.transform_method == "scaledlogit":
            self.scaler = ScaledLogitScaler()
            self.scaler.fit(self.y)
            self.transformed_y = self.scaler.transform(self.y)
        elif self.transform_method == "minmax":
            self.scaler = MinMaxScaler()
            self.transformed_y = self.scaler.fit_transform(self.y)
        else:
            self.transformed_y = self.y

    def get_benchmark_evaluation(self):
        """
        Get Benchmark Methods' (Naive, Searsonal Naive and Mean) evaluation metrics.
        """
        naive_pred = naive_method(self.data[self.y_var])
        mean_pred = mean_method(self.data[self.y_var])
        snaive_pred = seasonal_naive_method(self.data[self.y_var])
        benchmark = pd.DataFrame()

        for idx, method in enumerate([naive_pred, mean_pred, snaive_pred]):
            metrics = calculate_evaluation(self.data[self.y_var], method)
            metrics_df = pd.DataFrame(metrics, index=[idx])
            benchmark = pd.concat([benchmark, metrics_df], axis=0)
        benchmark.index = ["naive", "mean", "seasonal naive"]

        self.benchmark = benchmark

    def stepwise_search(self,
                        d: Union[int, None] = None,
                        d_s: Union[int, None] = None) -> dict:
        """
        Perform stepwise search for the best SARIMAX model.

        Args:
            d : the order of differencing
            D : the order of seasonal differencing

        Returns:
            dict: Dictionary containing the parameters of the best model.
        """
        self.stepwise_fit = auto_arima(self.transformed_y.iloc[:self.training_size],
                                       X=self.exog.iloc[:self.training_size],
                                       start_p=0, start_q=0,
                                       max_p=5, max_q=5, m=12,
                                       start_P=0, seasonal=True,
                                       d=d, D=d_s, trace=self.verbose,
                                       error_action='ignore',
                                       suppress_warnings=True,
                                       stepwise=True)
        self.stepwise_model = self.stepwise_fit.get_params()

    def manual_search(self,
                      params: Union[Dict, None] = None) -> list:
        """
        Perform manual search for SARIMAX models.

        Args:
            params (list): List of SARIMAX model parameters.

        Returns:
            list: List containing SARIMAX model results.
        """

        if not params:
            params = generate_search_params(max_p=6, max_q=6, max_ps=3, max_qs=3)

        self.manual_search_results = []
        with tqdm(total=len(params)) as pbar:
            for param in params:
                try:
                    mod = SARIMAX(self.transformed_y.iloc[:self.training_size],
                                  exog=self.exog[:self.training_size],
                                  order=param[0],
                                  seasonal_order=param[1])
                    res = mod.fit(disp=False)

                    # pred = self.get_prediction_df(
                    #     res, steps=self.test_size, exog=self.exog[-self.test_size:])
                    # if self.transform_method is not None:
                    #     pred["inv_pred"] = self.scaler.inverse_transform(
                    #         pred["pred"])
                    # eval_metrics = calculate_evaluation(
                    #     self.y.values[-self.test_size:], pred.inv_pred.values[-self.test_size:])
                    self.manual_search_results.append(
                        (res, res.aic, param))
                except Exception as e:
                    print(f"Running {param} encountered an errror: ", e)
                    continue
                pbar.update(1)

        self.manual_search_results.sort(key=lambda x: x[1])
        return self.manual_search_results

    @staticmethod
    def get_prediction_df(mod,
                          steps: int,
                          exog) -> pd.DataFrame:
        """
        Generate a dataframe that contains prediction/forecasts.
        """
        pred = (mod.get_prediction()
                   .summary_frame(alpha=0.05)
                   .rename({"mean": "pred"}, axis=1))
        if steps != 0:
            forecast = (mod.get_forecast(
                steps=steps, exog=exog, dynamic=True).summary_frame(alpha=0.05).
                rename({"mean": "pred"}, axis=1))

            pred_stats = pd.concat([pred, forecast], axis=0)
        else:
            pred_stats = pred

        return pred_stats

class OtherTSToolKits(SARIMAXData):
    def __init__(self, country: str,
                 y_var: str,
                 exog_var: list,
                 transform_method: str,
                 training_ratio: float,
                 method: str,
                 trends_data_folder: str = os.path.join(
                     os.getcwd(), "data", "tourism", "trends"),
                 covid_idx_path: str = os.path.join(
                     os.getcwd(), "data", "tourism", "oceania_covid_stringency.csv")):
        super().__init__(country, y_var, exog_var, transform_method,
                         training_ratio, trends_data_folder, covid_idx_path)
        if method not in ["prophet", "stl"]:
            raise ValueError("No Such Methods exsits")
        self.method = method

    def stl_forecast(self, **kwargs):
        """ 
        Fit a STL model.
        """
        if self.method != "stl":
            raise ValueError("Not applicable for the chosen method")

        # Perform STL analysis
        stl = STL(self.data[self.y_var], **kwargs)
        res = stl.fit()

        # TO DO:
        # 1. Fit residual of STL decomposition by pm.auto
        # 2. Using auto order to fit into STLForecast and calling ARIMA method

    def prophet_analysis(self):
        if self.method != "prophet":
            raise ValueError("Not applicable for the chosen method")

        # Initialize and fit Prophet model
        model = Prophet()
        prophet_data = pd.DataFrame()
        prophet_data["ds"] = self.data["date"]
        prophet_data["y"] = self.transformed_y
        if self.exog_var:
            for var in self.exog_var:
                prophet_data[var] = self.data[var]
                model.add_regressor(var)

        training_data = prophet_data.iloc[:self.training_size]
        model.fit(training_data)

        # Make future predictions
        future = model.make_future_dataframe(periods=self.test_size, freq="MS")
        for var in self.exog_var:
            future[var] = prophet_data[var]

        forecast = model.predict(future)
        if self.transform_method == "scaledlogit":
            forecast["inverse_yhat"] = self.scaledlogit.inverse_transform(
                forecast["yhat"])

        return forecast
