import os
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy

#!pip install pmdarima
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
from pmdarima import model_selection
from pmdarima import auto_arima


class SARIMAXPipeline:
    def __init__(self,
                 data: pd.DataFrame,
                 y: str, exog_var: str,
                 transform_method: str,
                 training_ratio=0.9):
        self.data = data
        self.y = y
        self.exog_var = exog_var
        self.exog = self.data[[self.exog_var]]
        self.transform_method = transform_method
        if transform_method not in ["scaledlogit", "minmax", None]:
            raise AttributeError("No such transformation exists.")
        self.training_ratio = training_ratio
        self.total_size = len(self.data)
        self.training_size = int(training_ratio * self.total_size)
        self.test_size = self.total_size - self.training_size
        print("training size : {}, testing size : {}".format(
            self.training_size, self.test_size))
        self.stepwise_model = None

    @staticmethod
    def scaled_logit_transform(series):
        upper, lower = series.max() + 1, series.min() - 1
        scaled_logit = np.log((series - lower)/(upper - series))

        return scaled_logit

    @staticmethod
    def inverse_scaled_logit(trans_series, upper, lower):
        exp = np.exp(trans_series)
        inv_series = (((upper - lower) * exp) / (1 + exp)) + lower
        return inv_series

    def transform(self):
        if self.transform_method == "scaledlogit":
            self.transformed_y = scaled_logit_transform(self.data[[self.y]])
        elif self.transform_method == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            self.minmax = MinMaxScaler()
            self.transformed_y = minmax.fit_transform(self.data[[self.y]])
        else:
            self.transformed_y = self.data[[self.y]]

    def stepwise_search(self) -> dict:
        stepwise_fit = auto_arima(self.transformed_y.iloc[:self.training_size+1],
                                  X=self.exog.iloc[:self.training_size+1],
                                  start_p=0, start_q=0,
                                  max_p=5, max_q=5, m=12,
                                  start_P=0, seasonal=True,
                                  d=0, D=1, trace=True,
                                  error_action='ignore',
                                  suppress_warnings=True,
                                  stepwise=True)
        print(stepwise_fit.summary())
        stepwise_fit.plot_diagnostics(figsize=(15, 12))
        plt.show()
        self.stepwise_model = stepwise_fit.get_params()

        return self.stepwise_model

    def manual_search(self, params):
        self.manual_search_results = []
        for param in params:
            try:
                mod = SARIMAX(self.transformed_y.iloc[:self.training_size+1],
                              exog=self.exog[:self.training_size+1],
                              order=param[0],
                              seasonal_order=param[1],
                              return_ssm=False)
                res = mod.fit(disp=False)
                self.manual_search_results.append((res, res.aic, param))
                print(
                    'Tried out SARIMAX{}x{} - AIC:{}'.format(param[0], param[1], round(res.aic, 2)))
            except Exception as e:
                print(e)
                continue
        return self.manual_search_results

    @staticmethod
    def get_prediction_df(mod, steps: int, exog) -> pd.DataFrame:

        pred = (mod.get_prediction().summary_frame(alpha=0.05)
                .rename({"mean": "train_pred"}, axis=1))
        forecast = (mod.get_forecast(
            steps=steps, exog=exog, dynamic=True).summary_frame(alpha=0.05).
            rename({"mean": "test_pred"}, axis=1))

        pred_stats = pd.concat([pred, forecast], axis=0)

        return pred_stats

    @staticmethod
    def compare_models(data,
                       models: list,
                       hyper_params=None):

        from pmdarima.model_selection import SlidingWindowForecastCV, cross_val_score

        if hyper_params is None:
            hyper_params = {
                "window_size": 12,
                "step": 6,
                "h": 12
            }

        cv = SlidingWindowForecastCV(window_size=hyper_params["window_size"],
                                     step=hyper_params["step"],
                                     h=hyper_params["h"])

        result = {
            "model": [],
            "cv_scores": [],
            "avg_error": [],
        }

        for model in models:
            model_cv_scores = cross_val_score(
                model, data, scoring='smape', cv=cv, verbose=2)
            model_avg_error = np.average(model_cv_scores)
            result["model"].append(model)
            result["cv_scores"].append(model_cv_scores)
            result["avg_error"].append(model_avg_error)

        return result