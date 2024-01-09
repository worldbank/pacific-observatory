import os
import sys
import itertools
import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

#!pip install pmdarima
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.forecasting.stl import STLForecast
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
from pmdarima import auto_arima
from pmdarima.model_selection import SlidingWindowForecastCV, cross_val_score
from prophet import Prophet

from .scaler import ScaledLogitScaler
from .ts_eval import *
from .data import *
from .ts_utils import *
from typing import Union, List, Dict

__all__ = [
    "SARIMAXPipeline",
    "OtherTSToolKits"
]

class SARIMAXPipeline(SARIMAXData):
    def __init__(self,
                 country: str,
                 y_var: str,
                 exog_var: list,
                 transform_method: str,
                 training_ratio=0.9,
                 verbose=True,
                 trends_data_folder: str = os.path.join(
                     os.getcwd(), "data", "tourism", "trends"),
                 covid_idx_path: str = os.path.join(os.getcwd(), "data", "tourism", "oceania_covid_stringency.csv")):
        """
        Initialize SARIMAXPipeline object.

        Args:
            y (str): The name of the column representing the time series variable.
            exog_var (list, optional): The list of the column names representing the exogenous variable.
            transform_method (str, optional): The name of the transformation method to apply to the time series.
            training_ratio (float, optional): The proportion of the data to use for training the model.
            verbose (bool): Logging the model running or not.

        Raises:
            AttributeError: If an invalid transformation method is specified.
        """
        super().__init__(country, y_var, exog_var,
                         training_ratio, trends_data_folder, covid_idx_path)
        if transform_method not in ["scaledlogit", "minmax", None]:
            raise AttributeError("No such transformation exists.")
        self.transform_method = transform_method
        self.verbose = verbose

        # Initialize the stepwise model
        self.stepwise_model = None
        self.manual_search_results = None

    def transform(self):

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

        print("training size : {}, testing size : {}".format(
            self.training_size, self.test_size))

        if self.transform_method == "scaledlogit":
            self.scaledlogit = ScaledLogitScaler()
            self.scaledlogit.fit(self.y)
            self.transformed_y = self.scaledlogit.transform(self.y)
        elif self.transform_method == "minmax":
            self.minmax = MinMaxScaler()
            self.transformed_y = self.minmax.fit_transform(self.y)
        else:
            self.transformed_y = self.y

    def get_benchmark_evaluation(self):

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
                        D: Union[int, None] = None) -> dict:
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
                                       d=d, D=D, trace=self.verbose,
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
            p, d, q = range(0, 3), range(0, 2), range(0, 3)
            P, D, Q, s = range(0, 3), range(0, 2), range(0, 3), [12]

            # list of all parameter combos
            pdq = list(itertools.product(p, d, q))
            seasonal_pdq = list(itertools.product(P, D, Q, s))
            params = list(itertools.product(pdq, seasonal_pdq))

        self.manual_search_results = []
        with tqdm(total=len(params)) as pbar:
            for param in params:
                try:
                    mod = SARIMAX(self.transformed_y.iloc[:self.training_size],
                                  exog=self.exog[:self.training_size],
                                  order=param[0],
                                  seasonal_order=param[1])
                    res = mod.fit(disp=False)
                    self.manual_search_results.append((res, res.aic, param))
                    if self.verbose:
                        logging.info(
                            'Tried out SARIMAX{}x{} - AIC:{}'.format(param[0], param[1], round(res.aic, 2)))
                except Exception as e:
                    print(e)
                    continue
                pbar.update(1)

        self.manual_search_results.sort(key=lambda x: x[1])
        return self.manual_search_results

    @staticmethod
    def get_prediction_df(mod, steps: int, exog) -> pd.DataFrame:

        pred = (mod.get_prediction()
                   .summary_frame(alpha=0.05)
                   .rename({"mean": "train_pred"}, axis=1))
        if steps != 0:
            forecast = (mod.get_forecast(
                steps=steps, exog=exog, dynamic=True).summary_frame(alpha=0.05).
                rename({"mean": "test_pred"}, axis=1))

            pred_stats = pd.concat([pred, forecast], axis=0)
        else:
            pred_stats = pred

        return pred_stats

    @staticmethod
    def compare_models(y,
                       exog: str,
                       models: list,
                       scoring="smape",
                       hyper_params: Union[Dict, None] = None,
                       verbose=0) -> dict:
        """
        Compare different SARIMAX models based on evaluation metrics.

        Args:
            y : Time series data.
            exog : Exogenous variables.
            models (list): List of SARIMAX models.
            scoring (str, optional): Scoring method for evaluation.
            hyper_params (dict, optional): Hyperparameters for cross-validation.
            verbose (int, optional): Verbosity level for evaluation.

        Returns:
            comparison_result (dict): Dictionary containing model comparison results.
        """

        if hyper_params is None:
            hyper_params = {
                "window_size": 12,
                "step": 1,
                "h": 12
            }

        cv = SlidingWindowForecastCV(window_size=hyper_params["window_size"],
                                     step=hyper_params["step"],
                                     h=hyper_params["h"])

        comparison_result = {
            "model": [],
            "cv_scores": [],
            "avg_error": [],
        }

        for model in models:
            try:
                model_cv_scores = cross_val_score(
                    model, y, exog, scoring=scoring, cv=cv, verbose=verbose)
                model_avg_error = np.nanmean(model_cv_scores)
                comparison_result["model"].append(model)
                comparison_result["cv_scores"].append(model_cv_scores)
                comparison_result["avg_error"].append(model_avg_error)
            except:
                pass

        return comparison_result


class OtherTSToolKits(SARIMAXData):
    def __init__(self, country: str,
                 y_var: str,
                 exog_var: list,
                 transform_method: str,
                 training_ratio: float,
                 method: str,
                 trends_data_folder: str = os.path.join(
                     os.getcwd(), "data", "tourism", "trends"),
                 covid_idx_path: str = os.path.join(os.getcwd(), "data", "tourism", "oceania_covid_stringency.csv")):
        super().__init__(country, y_var, exog_var, transform_method,
                         training_ratio, trends_data_folder, covid_idx_path)
        if method not in ["prophet", "stl"]:
            raise ValueError("No Such Methods exsits")
        self.method = method

    def stl_forecast(self, **kwargs):
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
            forecast["inverse_yhat"] = self.scaledlogit.inverse_transform(forecast["yhat"])

        return forecast
