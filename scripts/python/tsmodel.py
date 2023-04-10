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
                 y_var: str, exog_var: list,
                 transform_method: str,
                 training_ratio=0.9):
        """
        Initialize SARIMAXPipeline object.

        Args:
            data (pd.DataFrame): The time series data.
            y (str): The name of the column representing the time series variable.
            exog_var (list, optional): The list of the column names representing the exogenous variable.
            transform_method (str, optional): The name of the transformation method to apply to the time series.
            training_ratio (float, optional): The proportion of the data to use for training the model.

        Raises:
            AttributeError: If an invalid transformation method is specified.
        """
        self.data = data
        self.y_var = y_var
        self.exog_var = exog_var
        self.training_ratio = training_ratio
        self.transform_method = transform_method

        # Check if the transformation method is valid
        if transform_method not in ["scaledlogit", "minmax", None]:
            raise AttributeError("No such transformation exists.")

        # Load the data
        self.y = self.data[[self.y_var]]
        self.exog = self.data[self.exog_var]

        self.total_size = len(self.data)
        self.training_size = int(training_ratio * self.total_size)
        self.test_size = self.total_size - self.training_size
        print("training size : {}, testing size : {}".format(
            self.training_size, self.test_size))

        # Initialize the stepwise model
        self.stepwise_model = None
        self.manual_search_results = None

    @staticmethod
    def scaledlogit_transform(series):
        upper, lower = series.max() + 1, series.min() - 1
        scaled_logit = np.log((series - lower)/(upper - series))

        return scaled_logit

    @staticmethod
    def inverse_scaledlogit(trans_series, upper, lower):
        exp = np.exp(trans_series)
        inv_series = (((upper - lower) * exp) / (1 + exp)) + lower
        return inv_series

    def transform(self):
        if self.transform_method == "scaledlogit":
            self.transformed_y = self.scaledlogit_transform(self.y)
        elif self.transform_method == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            self.minmax = MinMaxScaler()
            self.transformed_y = minmax.fit_transform(self.y)
        else:
            self.transformed_y = self.y

    def stepwise_search(self, d: int = None, D: int= None) -> dict:
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
                                  d=d, D=D, trace=True,
                                  error_action='ignore',
                                  suppress_warnings=True,
                                  stepwise=True)
        print(self.stepwise_fit.summary())
        self.stepwise_fit.plot_diagnostics(figsize=(15, 12))
        plt.show()
        self.stepwise_model = self.stepwise_fit.get_params()

        return self.stepwise_model

    def manual_search(self, params):
        self.manual_search_results = []
        for param in params:
            try:
                mod = SARIMAX(self.transformed_y.iloc[:self.training_size],
                              exog=self.exog[:self.training_size],
                              order=param[0],
                              seasonal_order=param[1])
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
    def compare_models(y, exog,
                       models: list,
                       scoring="smape",
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

        comparison_result = {
            "model": [],
            "cv_scores": [],
            "avg_error": [],
        }

        for model in models:
            model_cv_scores = cross_val_score(
                model, y, exog, scoring=scoring, cv=cv, verbose=2)
            model_avg_error = np.average(model_cv_scores)
            comparison_result["model"].append(model)
            comparison_result["cv_scores"].append(model_cv_scores)
            comparison_result["avg_error"].append(model_avg_error)

        return comparison_result
    

def varma_search(data: pd.DataFrame, var_name: list, exog: pd.DataFrame):

    from statsmodels.tsa.api import VARMAX
    from sklearn.model_selection import ParameterGrid

    param_grid = {'p': [1, 2, 3], 'q': [1, 2, 3], 'tr': ['n', 'c', 't', 'ct']}
    pg = list(ParameterGrid(param_grid))

    model_res = {
        "model": [],
        "result": []
    }
    for idx, params in enumerate(pg):
        print(f' Running for {params}')
        p = params.get('p')
        q = params.get('q')
        tr = params.get('tr')
        model = VARMAX(data[var_name],
                       exog=exog,
                       order=(p, q), trend=tr).fit(disp=False)
        model_res["model"].append((p, q, tr))
        model_res["result"].append(model.aic)

    return model_res