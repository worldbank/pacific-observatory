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

def sarimax(series, exog, all_param):
    results = []
    for param in all_param:
        try:
            mod = SARIMAX(series,
                          exog=exog,
                          order=param[0],
                          seasonal_order=param[1],
                          return_ssm=False)
            res = mod.fit()
            results.append((res, res.aic, param))
            print(
                'Tried out SARIMAX{}x{} - AIC:{}'.format(param[0], param[1], round(res.aic, 2)))
        except Exception as e:
            print(e)
            continue
    return results


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