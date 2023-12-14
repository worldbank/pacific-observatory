import os
import pandas as pd
import numpy as np
import chardet
import logging
import statsmodels
import sklearn
from sklearn.model_selection import ParameterGrid
from statsmodels.tsa.api import VARMAX
import statsmodels.formula.api as smf
from .scaler import ScaledLogitScaler
from .utsmodel import SARIMAXData
from .ts_eval import *
from .ts_utils import *
from .data import *

__all__ = [
    "RatioPipe"
]

class VARPipeline(MultiTSData):
    def __init__(self,
                 country: str,
                 y_var: str,
                 exog_var: list,
                 transform_method: str,
                 training_ratio: float,
                 trends_data_folder: str = TRENDS_DATA_FOLDER,
                 covid_idx_path: str = COVID_DATA_PATH,
                 aviation_path: str = DEFAULT_AVIATION_DATA_PATH):
        super().__init__(country, y_var, exog_var, transform_method,
                         training_ratio, trends_data_folder, covid_idx_path)
        self.var_name = var_name
        self.x1, self.x2 = var_name
        self.exog = exog

    def test_stationarity(self):
        adf_df = get_adf_df(self.data[self.var_name], self.var_name)

        order = 0
        while np.average(adf_df["p-value"]) > 0.05 and order < 2:
            self.stationary_data = self.data[self.var_name].diff().dropna()
            adf_df = get_adf_df(self.stationary_data, self.var_name)
            print(f"order = {order}: no stationarity obtained.")
            order += 1
            if order >= 2:
                break
        else:
            display(adf_df)
            print(f"order = {order}: stationarity obtained.")

    def varma_search(self, verbose=False):

        param_grid = {'p': [1, 2, 3],
                      'q': [1, 2, 3],
                      'tr': ['n', 'c', 't', 'ct']}
        pg = list(ParameterGrid(param_grid))

        model_res = {
            "model": [],
            "result": []
        }

        for idx, params in enumerate(pg):
            if verbose:
                print(f' Running for {params}')
            p = params.get('p')
            q = params.get('q')
            tr = params.get('tr')
            model = VARMAX(self.scaled,
                           exog=self.data[self.exog],
                           order=(p, q),
                           trend=tr).fit(disp=False)
            model_res["model"].append((p, q, tr))
            model_res["result"].append(model.aic)

        self.model_res_df = (pd.DataFrame(model_res)
                             .sort_values(by="result", ascending=True))
        self.p, self.q, self.tr = self.model_res_df.iloc[0, 0]
        print(f"Best P, Q, Trend Combination: {self.p, self.q, self.tr}")

    def fit(self):
        self.mod = VARMAX(self.scaled,
                          exog=self.data[self.exog],
                          order=(self.p, self.q),
                          trend=self.tr).fit(disp=False)
        print(self.mod.summary())

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
        display(benchmark)


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

        self.res = smf.ols(
            formula,
            data=self.model_data).fit(cov_type='HAC', cov_kwds={"maxlags": maxlags,
                                                                "use_correction": True})

    def get_prediction(self):
        pred_df = self.res.get_prediction().summary_frame()
        select_cols = ["date", "ratio", self.x1, self.x2]
        self.pred_df = pd.concat([self.model_data[select_cols], pred_df], axis=1)
        self.pred_df["pred_mean"] = self.pred_df["mean"] * self.pred_df[self.x2]

        return self.pred_df
