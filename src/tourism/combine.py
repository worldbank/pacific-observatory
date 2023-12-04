import pandas as pd
import numpy as np
import scipy


def calculate_mse(predictions_df: pd.DataFrame, method: str) -> pd.Series:
    total = predictions_df["total"]
    prediction = predictions_df[method]
    mse = np.square(total - prediction).cumsum() / (predictions_df.index + 1)
    return mse


def calculate_rpw(predictions_df: pd.DataFrame, methods: list) -> pd.Series:
    mse_dict = {method: calculate_mse(predictions_df, method)
                for method in methods}
    denominator = sum(1 / mse_dict[method] for method in methods)
    rpw_dict = {}
    for method in methods:
        numerator = 1 / mse_dict[method]
        omega = numerator / denominator
        rpw_dict[method] = omega
    return pd.Series(rpw_dict)


def get_rpw(pred_df: pd.DataFrame,
            methods: list = ["sarimax", "var", "lf"]) -> pd.Series:
    predictions_df = pred_df.copy()
    rpw_series = calculate_rpw(predictions_df, methods)

    combo_cols = []
    for method in methods:
        weight = str(method) + "_weight"
        predictions_df[weight] = predictions_df[method] * rpw_series[method]
        combo_cols.append(weight)

    rpw_pred = predictions_df[combo_cols].sum(axis=1)
    rpw = pd.DataFrame(rpw_series.to_dict())
    rpw.columns = ["rpw_" + str(col) for col in rpw.columns]

    return rpw_pred, rpw


def get_constrained_ls(y: pd.DataFrame,
                       X: pd.DataFrame) -> np.array:

    from scipy.optimize import nnls, minimize

    A, b = np.array(X), np.array(y)
    x0, norm = nnls(A, b)

    def f(x, A, b):
        return np.linalg.norm(A.dot(x) - b)

    mini = minimize(f, x0, args=(A, b), method='SLSQP',
                    bounds=[[0, np.inf]], ## Only set the lb
                    constraints={'type': 'eq', 'fun': lambda x:  np.sum(x)-1})
    estimates = mini.x
    pred = A.dot(estimates)
    
    return estimates, pred