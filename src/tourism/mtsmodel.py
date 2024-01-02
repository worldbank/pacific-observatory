import os
import pandas as pd
import numpy as np
import logging
import statsmodels
import sklearn
from sklearn.model_selection import ParameterGrid
from statsmodels.tsa.api import VARMAX
import statsmodels.formula.api as smf
from statsmodels.tsa.stattools import coint
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
            raise ValueError("`y_var` should be list.")
        self.exog = exog_var
        self.transformation = None
        self.is_stationary = None
        self.is_cointegrated = None

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

    @staticmethod
    def test_cointegration(y0, y1) -> bool:
        """
        Call coint to test cointegration for two given time series y0 and y1.
        """
        result = coint(y0, y1)
        return (result[1] < 0.05)

    def determine_method(self):
        """
        Determine VARMA or VECM based on integration/cointegration
        """
        transformations = {
            'original': self.data[self.y_var].dropna(),
            'diff': self.data[self.y_var].diff().dropna(),
            # 'log_diff': np.log(self.data[self.y_var]+1).diff().dropna()
        }

        for method, data in transformations.items():
            if self.test_stationarity(data, self.y_var):
                self.transformation = method
                self.transformed_y = data
                self.exog_data = self.data.loc[self.transformed_y.index,
                                               self.exog_var]
                print(f"{method.capitalize()} series is stationary.")
                break

        if not self.transformation:
            print("Unable to achieve stationarity with the specified transformations.")
            # Split data into series for cointegration test
            self.y0_data, self.y1_data = self.data[self.y_var]
            self.is_cointegrated = self.test_cointegration(
                self.y0_data, self.y1_data)
            if self.is_cointegrated:
                self.method = "VECM"
        else:
            self.method = "VARMAX"

    def grid_search(self):

        param_grid = {'p': [1, 2, 3],
                      'q': [1, 2, 3],
                      'tr': ['n', 'c', 't', 'ct']}
        pg = list(ParameterGrid(param_grid))

        grid_search_dict = {
            "model": [],
            "aic": []
        }
        if self.method == "VARMAX":
            for idx, params in enumerate(pg):
                p = params.get('p')
                q = params.get('q')
                tr = params.get('tr')
                model = VARMAX(endog=self.transformed_y,
                            exog=self.exog_data,
                            order=(p, q),
                            trend=tr)
                res = model.fit(disp=False)
                grid_search_dict["model"].append((p, q, tr))
                grid_search_dict["aic"].append(res.aic)

            self.grid_search_res = (pd.DataFrame(grid_search_dict)
                                  .sort_values(by="aic")
                                  .reset_index(drop=True))
            self.p, self.q, self.tr = self.grid_search_res["model"][0]
        
        elif self.method == "VECM":
            pass
        else:
            raise ValueError("Not Conducting Grid Search")

 

    def fit(self):
        if self.method == "VARMAX":
            self.mod = VARMAX(endog=self.transformed_y,
                              exog=self.exog_data,
                              order=(self.p, self.q),
                              trend=self.tr).fit(disp=False)
        elif self.method == "VECM":
            pass


    def get_fittedvalues(self):
        self.fittedvalues = self.mod.fittedvalues
        rev_vals = []
        for raw_val in self.fittedvalues[self.x1]:
            rev_val = inverse_scaledlogit(
                raw_val, upper=self.data[self.x1].max()+1,
                lower=self.data[self.x1].min()-1
            )
            rev_vals.append(rev_val)
        self.data["pred_total"] = rev_vals

    def evaluate_models(self):
        naive_pred = naive_method(self.data[self.x1])
        mean_pred = mean_method(self.data[self.x1])

        benchmark = pd.DataFrame()
        for name, pred in zip(["naive", "mean", "VAR (scaled)"], [naive_pred, mean_pred, self.data.pred_total]):
            eval = calculate_evaluation(self.data[self.x1], pred)
            eval_df = pd.DataFrame(eval, index=[name])
            benchmark = pd.concat([benchmark, eval_df], axis=0)


class RatioPipe(MultiTSData):
    def __init__(self, country,
                 y_var,
                 exog_var,
                 transform_method,
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
        super().__init__(country, y_var, exog_var, transform_method, training_ratio)
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
