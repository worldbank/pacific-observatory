"""
The mtsmodel module provides 

Last updated:
    2024-02-02
"""
from collections import Counter
import pandas as pd
import numpy as np
from sklearn.model_selection import ParameterGrid
from statsmodels.tsa.api import VARMAX
import statsmodels.formula.api as smf
from statsmodels.tsa.vector_ar.vecm import select_order, VECM
from .scaler import ScaledLogitScaler, Differencing
from .ts_eval import (naive_method, mean_method,
                      seasonal_naive_method, calculate_evaluation)
from .ts_utils import cointegration_test, get_adf_df
from .data import (MultiTSData, TRENDS_DATA_FOLDER,
                   COVID_DATA_PATH, DEFAULT_AVIATION_DATA_PATH)

__all__ = [
    "VARPipeline",
    "RatioPipe"
]


class VARPipeline(MultiTSData):
    """
    The wrapper to fit VAR(MA)X/VECM based on cointegration 
        and stationarity.

    To use: 
        model = VARPipeline(country="samoa",
                    y_var=["total", "seats_arrival_intl"],
                    exog_var=["covid", "stringency_index", "samoa_travel"])
        model.read_and_merge()
        model.determine_analysis_method()
        model.fit()
    """
    def __init__(self,
                 country: str,
                 y_var: str,
                 exog_var: list,
                 trends_data_folder: str = TRENDS_DATA_FOLDER,
                 covid_idx_path: str = COVID_DATA_PATH,
                 aviation_path: str = DEFAULT_AVIATION_DATA_PATH):
        """
        Initialize SARIMAXPipeline object.

        Args:
          country (str): The name of the country being modelled.
          y_var (list): The name of the column representing the time series variable.
          exog_var (list, optional): The list of the column names representing 
            the exogenous variable.

        Raises:
            AttributeError: If y_var does not have two variables in a list.
        """
        super().__init__(country, y_var, exog_var)
        if isinstance(y_var, list) and len(y_var) != 2:
            self.y_var = y_var
            self.y0, self.y1 = y_var
        else:
            raise AttributeError("`y_var` should a list of two variables.")
        self.exog = exog_var
        self.raw_data = None
        self.transformed_data = None
        self.scaler = None
        self.differencer = None
        self.method = None
        self.transformation = []
        self.is_stationary = None
        self.is_cointegrated = None
        self.test_results = {'stationarity': {}, 'cointegration': {}}
        self.fitted_models = None
        self.prediction_dfs = None

    @staticmethod
    def test_stationarity(df, y_var) -> bool:
        """
        Test for cointegration between two time series
        """
        adf_df = get_adf_df(df, y_var)

        return np.all(adf_df["p-value"] <= 0.05)

    def transform_data(self):
        """
        Transform the time series data based on the specified method.
        """
        transformed_data = {}
        self.scaler = ScaledLogitScaler()
        self.differencer = Differencing()
        original = self.data[self.y_var].dropna()
        transformed_data["original"] = original
        transformed_data["difference"] = self.differencer.transform(original)
        self.scaler.fit(original)
        transformed_data["scaledlogit"] = self.scaler.transform(original)
        return transformed_data

    def determine_analysis_method(self):
        """
        Determine VARMA or VECM based on stationarity and cointegration
        """
        self.raw_data = self.data[self.y_var]
        self.transformed_data = self.transform_data()

        for t_type, data in self.transformed_data.items():
            stationarity = self.test_stationarity(data, self.y_var)
            self.test_results['stationarity'][t_type] = stationarity
            coint_stats = cointegration_test(data)
            self.test_results["cointegration"][t_type] = coint_stats

        any_stationarity = any(self.test_results["stationarity"].values())

        if any_stationarity:
            self.method = "VARMAX"
            true_keys = [
                key for key, value in self.test_results["stationarity"].items() if value]
            self.transformation.extend(true_keys)

        else:
            cointegration_keys = [
                t_type
                for t_type, object in self.test_results["cointegration"].items()
                if any(stat["Significance"] for stat in object.values())
            ]

            # Check if there's any cointegration
            any_cointegration = bool(cointegration_keys)

            if any_cointegration:
                self.is_cointegrated = True
                self.method = "VECM"
                self.transformation.extend(cointegration_keys)
            else:
                print("Data does not meet the requirements for VARMAX or VECM")

    @staticmethod
    def fit_varma(endog_data, exog_data):
        param_grid = {'p': [1, 2],
                      'q': [1, 2],
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
        (p, q), tr = sorted_results[0]["model"]

        model = VARMAX(endog=endog_data,
                       exog=exog_data,
                       order=(p, q),
                       trend=tr)
        fitted_model = model.fit(disp=False)
        return fitted_model, grid_search_results

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
        self.fitted_models = {}
        self.prediction_dfs = {}
        for t_type, data in self.transformed_data.items():
            if t_type in self.transformation:
                endog_data = data
                select_idx = endog_data.index
                exog_data = self.data[self.exog_var].iloc[select_idx]

                if self.method == "VARMAX":
                    mod, _ = self.fit_varma(endog_data, exog_data)
                    self.fitted_models[t_type] = mod
                elif self.method == "VECM":
                    mod = self.fit_vecm(endog_data, exog_data)
                    self.fitted_models[t_type] = mod

                predict_df = pd.DataFrame(mod.model.endog, columns=self.y_var)
                predict_df["pred_total"] = np.NaN
                if self.method == "VARMAX":
                    predict_df.loc[mod.model.k_ar:,
                                   "pred_total"] = mod.fittedvalues.iloc[:, 0].tolist()
                predict_df.loc[mod.model.k_ar:,
                               "pred_total"] = mod.fittedvalues[:, 0]
                predict_df['date'] = pd.date_range(
                    start="2019-01-01", periods=len(predict_df), freq='MS')
                self.prediction_dfs[t_type] = predict_df

    def evaluate_models(self):
        """
        Compare models to benchmark evaluation methods.

        Return:
            benchmark (pd.DataFrame): contains `naive` and `mean` method for forecasting.
        """
        naive_pred = naive_method(self.data[self.y0])
        mean_pred = mean_method(self.data[self.y0])

        benchmark = pd.DataFrame()
        if len(self.prediction_dfs) == 1:
            fittedvalues = self.prediction_dfs[self.transformation[0]
                                               ]["pred_total"]
            for name, pred in zip(["naive", "mean", "VAR (scaled)"],
                                  [naive_pred, mean_pred, fittedvalues]):
                eval_metrics = calculate_evaluation(self.data[self.y0], pred)
                eval_df = pd.DataFrame(eval_metrics, index=[name])
                benchmark = pd.concat([benchmark, eval_df], axis=0)

        return benchmark


class RatioPipe(MultiTSData):
    """
    The Wrapper to fit OLS (with HAC errors) on Adjusted Ratio 
        (actual visitor/aviation capacity).

    To use:
        model = RatioPipe(country=country,
                    y_var="total",
                    exog_var=["covid", "stringency_index", "samoa_travel"])
        model.read_and_merge()
        model.transform()
        model.fit(formula="ratio~covid * stringency_index+C(quarter)+" +
                str(country) + "_travel")
        pred_df = model.get_prediction()
        model.get_benchmark_evaluation()
    """
    def __init__(self, country,
                 y_var,
                 exog_var,
                 x2: str = "seats_arrivals_intl"):
        """
        Initialize RatioPipe object.

        Args:
            country (str): The country.
            y_var (str): The dependent variable.
            x2 (str, optional): The variable with `y_var` to produce ratio. Defaults to 
                `seats_arrivals_intl`.
            exog_var (str): The exogenous variable.
            transform_method (str): The transformation method.
            training_ratio (float): The training ratio.
        """
        super().__init__(country, y_var, exog_var)
        self.x1 = y_var
        self.x2 = x2
        self.model = None
        self.model_data = None
        self.res = None
        self.prediction = None
        self.benchmark = None

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
        if maxlags is None:
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
        self.prediction = pd.concat(
            [self.model_data[select_cols], pred_df], axis=1).dropna()
        self.prediction["pred_mean"] = self.prediction["mean"] * \
            self.prediction[self.x2]

        return self.prediction

    def get_benchmark_evaluation(self):
        """
        The function compares the ratio apparoch with other benchmark methods.
        """
        naive_pred = naive_method(self.prediction[self.x1])
        mean_pred = mean_method(self.prediction[self.x1])
        snaive_pred = seasonal_naive_method(self.prediction[self.x1])

        benchmark = pd.DataFrame()
        for idx, pred in enumerate([naive_pred, mean_pred,
                                    snaive_pred, self.prediction["pred_mean"]]):
            metrics = calculate_evaluation(self.prediction[self.x1], pred)
            metrics_df = pd.DataFrame(metrics, index=[idx])
            benchmark = pd.concat([benchmark, metrics_df], axis=0)
        benchmark.index = ["naive", "mean", "seasonal naive", "ratio"]

        self.benchmark = benchmark
