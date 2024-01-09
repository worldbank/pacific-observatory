import os
import pandas as pd
import numpy as np
import logging
import statsmodels
import sklearn
from collections import Counter
from sklearn.model_selection import ParameterGrid
from statsmodels.tsa.api import VARMAX
import statsmodels.formula.api as smf
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import select_order, VECM, coint_johansen
from .scaler import ScaledLogitScaler
from .utsmodel import SARIMAXData
from .ts_eval import *
from .ts_utils import *
from .data import *

__all__ = [
    "VARPipeline",
    "RatioPipe"
]


class VARPipeline(MultiTSData):
    def __init__(self,
                 country: str,
                 y_var: str,
                 exog_var: list,
                 training_ratio: float,
                 trends_data_folder: str = TRENDS_DATA_FOLDER,
                 covid_idx_path: str = COVID_DATA_PATH,
                 aviation_path: str = DEFAULT_AVIATION_DATA_PATH):
        super().__init__(country, y_var, exog_var, training_ratio)
        if isinstance(y_var, list):
            self.y_var = y_var
            self.y0, self.y1 = y_var
        else:
            raise ValueError("`y_var` should a list of two variables.")
        self.exog = exog_var
        self.transformation = None
        self.is_stationary = None
        self.is_cointegrated = None
        self.test_results = {'stationarity': {}, 'cointegration': {}}

    @staticmethod
    def test_stationarity(df, y_var) -> bool:
        """
        Test for cointegration between two time series
        """
        adf_df = get_adf_df(df, y_var)

        if np.all(adf_df["p-value"] <= 0.05):
            return True
        else:
            return False


    def transform_data(self, transformation='original'):
        """
        Transform the time series data based on the specified method.
        """
        if transformation == 'original':
            return self.data[self.y_var].dropna()
        elif transformation == 'difference':
            return self.data[self.y_var].diff().dropna()
        else:
            raise ValueError(f"Unknown transformation method: {transformation}")

    def determine_analysis_method(self):
        """
        Determine VARMA or VECM based on stationarity and cointegration
        """
        transformations = {
            'original': self.transform_data(transformation='original'),
            'difference': self.transform_data(transformation='difference')
        }

        for transform_type, data in transformations.items():
            stationarity = self.test_stationarity(data, self.y_var)
            self.test_results['stationarity'][transform_type] = stationarity
            coint_stats = cointegration_test(data)
            self.test_results["cointegration"][transform_type] = coint_stats

        any_stationarity = any(self.test_results["stationarity"].values())
        
        if any_stationarity:
            self.method = "VARMAX"
            true_keys = [key for key, value in self.test_results["stationarity"].items() if value]
            self.transformation = "original" if len(true_keys) > 1 else true_keys[0]

        else:
            cointegration_keys = [
                transformed_type 
                for transformed_type, object in self.test_results["cointegration"].items() 
                if any(stat["Significance"] for stat in object.values())
            ]

            # Check if there's any cointegration
            any_cointegration = bool(cointegration_keys)

            if any_cointegration:
                self.is_cointegrated = True
                self.method = "VECM"
                self.transformation = "original" if len(cointegration_keys) > 1 else cointegration_keys[0] 
            else:
                print("Data does not meet the requirements for VARMAX or VECM")

    @staticmethod
    def select_var_order(endog_data, exog_data):
        param_grid = {'p': [1, 2, 3],
                      'q': [1, 2, 3],
                      'tr': ['n', 'c', 't', 'ct']}
        models = [VARMAX(endog=endog_data,
                         exog=exog_data,
                         order=(params['p'], params['q']),
                         trend=params['tr'])
                  for params in ParameterGrid(param_grid)]

        grid_search_results = [{
            "model": (model.order, model.trend),
            "aic": model.fit(disp=False).aic
        } for model in models]

        sorted_results = sorted(grid_search_results, key=lambda x: x['aic'])
        return sorted_results
    
    @staticmethod
    def fit_vecm(endog_data, exog_data):
        """
        Fit a VECM model to the data and return the fitted model.
        """
        orders = select_order(endog_data, exog=exog_data, maxlags=5)
        # Extract values and count occurrences
        order_counts = Counter(orders.selected_orders.values())
        selected_order = order_counts.most_common(1)[0][0]

        model = VECM(endog_data,
                     exog=exog_data,
                     k_ar_diff=selected_order,
                     coint_rank=1)
        fitted_model = model.fit()
        return fitted_model


    def fit(self):
        self.endog_data = self.transform_data(transformation=self.transformation)
        select_idx = self.endog_data.index 
        self.exog_data = self.data[self.exog_var].iloc[select_idx]

        if self.method == "VARMAX":
            self.mod = VARMAX(endog=self.endog_data,
                              exog=self.exog_data,
                              order=(self.p, self.q),
                              trend=self.tr).fit(disp=False)
        elif self.method == "VECM":
            self.mod = self.fit_vecm(self.endog_data, self.exog_data)

    def get_fittedvalues(self):
        if self.transformation == 'original':
            self.fittedvalues = self.mod.fittedvalues
        elif self.transformation == 'difference':
            pass


    def evaluate_models(self):
        naive_pred = naive_method(self.data[self.y0])
        mean_pred = mean_method(self.data[self.y0])

        benchmark = pd.DataFrame()
        for name, pred in zip(["naive", "mean", "VAR (scaled)"], [naive_pred, mean_pred, self.data.fittedvalues]):
            eval = calculate_evaluation(self.data[self.y0], pred)
            eval_df = pd.DataFrame(eval, index=[name])
            benchmark = pd.concat([benchmark, eval_df], axis=0)


class RatioPipe(MultiTSData):
    def __init__(self, country,
                 y_var,
                 exog_var,
                 training_ratio,
                 x2: str = "seats_arrivals_intl"):
        """
        Initialize RatioPipe object.

        Args:
            country (str): The country.
            y_var (str): The dependent variable.
            x2 (str, optional): The variable with `y_var` to produce ratio. Defaults to "seats_arrivals_intl".
            exog_var (str): The exogenous variable.
            transform_method (str): The transformation method.
            training_ratio (float): The training ratio.
        """
        super().__init__(country, y_var, exog_var, training_ratio)
        self.x1 = y_var
        self.x2 = x2

    def transform(self):
        """
        Transform data by calculating the ratio and adjusting abnormal values.
        """

        self.model_data = (self.data[self.data.date >= "2019-01-01"]
                           .reset_index(drop=True))
        self.model_data["quarter"] = self.model_data["date"].dt.quarter
        ratios = []
        for x1, x2 in zip(self.model_data[self.x1], self.model_data[self.x2]):
            if x2 == 0 or x1 == 0:
                ratio = 0
            else:
                ratio = x1/x2
            ratios.append(ratio)
        # Adjust the ratio ex post
        for idx, ratio in enumerate(ratios):
            if ratio >= 1:
                print(f"Abnormal value produced with a value of {ratio}.")
                ratios[idx] = ((ratios[idx-1] + ratios[idx+1]))/2
        self.model_data["ratio"] = ratios

    def fit(self,
            formula: str,
            maxlags: int = None):
        """
        Fit the model using OLS.

        Args:
        - formula (str): The formula for the OLS model.
        - maxlags (int, optional): The maximum lag order. Defaults to None.

        """
        if maxlags == None:
            maxlags = int(4 * (len(self.model_data)/100) ** (2/9)) + 1

        self.model = smf.ols(
            formula,
            data=self.model_data)

        self.res = self.model.fit(cov_type='HAC',
                                  cov_kwds={"maxlags": maxlags,
                                            "use_correction": True})

    def get_prediction(self):
        pred_df = self.res.get_prediction().summary_frame()
        select_cols = ["date", "ratio", self.x1, self.x2]
        self.pred_df = pd.concat(
            [self.model_data[select_cols], pred_df], axis=1).dropna()
        self.pred_df["pred_mean"] = self.pred_df["mean"] * \
            self.pred_df[self.x2]

        return self.pred_df

    def get_benchmark_evaluation(self):
        naive_pred = naive_method(self.pred_df[self.x1])
        mean_pred = mean_method(self.pred_df[self.x1])
        snaive_pred = seasonal_naive_method(self.pred_df[self.x1])

        benchmark = pd.DataFrame()
        for idx, method in enumerate([naive_pred, mean_pred, snaive_pred, self.pred_df["pred_mean"]]):
            metrics = calculate_evaluation(self.pred_df[self.x1], method)
            metrics_df = pd.DataFrame(metrics, index=[idx])
            benchmark = pd.concat([benchmark, metrics_df], axis=0)
        benchmark.index = ["naive", "mean", "seasonal naive", "ratio"]

        self.benchmark = benchmark
