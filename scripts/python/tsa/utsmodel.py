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
from .ts_eval import *


class SARIMAXData:
    def __init__(self,
                 country: str,
                 data=None):
        self.country = country
        self.country_data_folder = os.getcwd() + "/data/tourism/" + str(country)
        self.trends_data_folder = os.getcwd() + "/data/tourism/trends"
        self.covid_idx_path = os.getcwd() + "/data/tourism/oceania_covid_stringency.csv"

    def read_country_data(self):
        country = (pd.read_csv(self.country_data_folder + "/intermediate/" +
                        str(self.country) + "_monthly_visitor.csv")
                  .drop("Unnamed: 0", axis=1))
        country.columns = [col.lower().replace(" ", "_") for col in country.columns]
        country["date"] = pd.to_datetime(country["date"])
        country["date"] = country["date"] - pd.offsets.MonthBegin()
        return country 

    def read_trends_data(self):
        trends = (pd.read_csv(self.trends_data_folder + "/trends_" +
                              str(self.country) + ".csv")
                  .drop("Unnamed: 0", axis=1))
        trends["date"] = pd.to_datetime(trends["date"])
        return trends 

    def read_covid_data(self):
        covid_idx = pd.read_csv(self.covid_idx_path).drop("Unnamed: 0", axis=1)
        covid_idx["date"] = pd.to_datetime(covid_idx["date"])
        covid_idx["covid"] = (covid_idx.date >= "2020-03-11").astype(int)
        return covid_idx
    
    def read_and_merge(self):
        country = self.read_country_data()
        trends = self.read_trends_data()
        covid_idx = self.read_covid_data()

        data = country.merge(covid_idx, how="left", on="date").fillna(0)
        data = data.merge(trends.iloc[:, [0, -3, -2, -1]],
                          how="left", on="date")
        data.columns = [col.lower().replace(" ", "_") for col in data.columns]       
        dropped_date_cols = [col for col in data.columns 
                             if col.startswith("year") or col.startswith("month")]
        dropped_idx = data[data["date"].diff() >= "32 days"].index - 1
        data = (data.drop(dropped_date_cols, axis=1)
                    .drop(dropped_idx, axis=0)
                    .reset_index()
                    .drop("index", axis=1)
                    .fillna(0))
        first_col = data.pop("date")
        data.insert(0, "date", first_col)
        self.data = data

class SARIMAXPipeline(SARIMAXData):
    def __init__(self,
                 country: str, 
                 data: pd.DataFrame,
                 y_var: str, exog_var: list,
                 transform_method: str,
                 training_ratio=0.9,
                 verbose=True):
        """
        Initialize SARIMAXPipeline object.

        Args:
            data (pd.DataFrame): The time series data.
            y (str): The name of the column representing the time series variable.
            exog_var (list, optional): The list of the column names representing the exogenous variable.
            transform_method (str, optional): The name of the transformation method to apply to the time series.
            training_ratio (float, optional): The proportion of the data to use for training the model.
            verbose (bool): Logging the model running or not.

        Raises:
            AttributeError: If an invalid transformation method is specified.
        """
        super().__init__(country, data)
        self.y_var = y_var
        self.exog_var = exog_var
        self.training_ratio = training_ratio
        self.transform_method = transform_method
        self.verbose = verbose

        # Check if the transformation method is valid
        if transform_method not in ["scaledlogit", "minmax", None]:
            raise AttributeError("No such transformation exists.")

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
       
        # Load the data
        self.y = self.data[[self.y_var]]
        self.exog = self.data[self.exog_var]
        self.total_size = len(self.data)
        self.training_size = int(self.training_ratio * self.total_size)
        self.test_size = self.total_size - self.training_size
        
        
        if self.data["date"][self.training_size-1] <= pd.Timestamp(2020, 3, 11):
            print("Training samples do not cover covid-19 periods. Instead, Run All Samples.")
            self.training_size = self.total_size
            self.test_size = 0
              
        print("training size : {}, testing size : {}".format(
            self.training_size, self.test_size))
        
        if self.transform_method == "scaledlogit":
            self.transformed_y = self.scaledlogit_transform(self.y)
        elif self.transform_method == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            self.minmax = MinMaxScaler()
            self.transformed_y = minmax.fit_transform(self.y)
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
                                  d=d, D=D, trace=self.verbose,
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
                if self.verbose:
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
        if steps != 0:
            forecast = (mod.get_forecast(
                steps=steps, exog=exog, dynamic=True).summary_frame(alpha=0.05).
                rename({"mean": "test_pred"}, axis=1))

            pred_stats = pd.concat([pred, forecast], axis=0)
        else:
            pred_stats = pred

        return pred_stats

    @staticmethod
    def compare_models(y, exog,
                       models: list,
                       scoring="smape",
                       hyper_params=None,
                       verbose=0):

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
                model, y, exog, scoring=scoring, cv=cv, verbose=verbose)
            model_avg_error = np.nanmean(model_cv_scores)
            comparison_result["model"].append(model)
            comparison_result["cv_scores"].append(model_cv_scores)
            comparison_result["avg_error"].append(model_avg_error)

        return comparison_result