import os
import warnings
import pandas as pd
import numpy as np
import scipy
import statsmodels
from statsmodels.tsa.stattools import (
    grangercausalitytests,
    kpss,
    adfuller
)
from statsmodels.tsa.vector_ar.vecm import coint_johansen

warnings.filterwarnings("ignore")


def cross_correlation(x, y) -> pd.DataFrame:
    """
    Computes the cross-correlation of two 1-dimensional sequences.

    Args:
        x: The first input sequence.
        y: The second input sequence.

    Returns:
        pd.DataFrame: Cross-correlation of x and y with two columns 'lags' and 'ccf'.
    """
    x = (x - x.mean()) / (x.std() * len(x))
    y = (y - y.mean()) / (y.std())
    result = np.correlate(x, y, mode='full')
    lags = scipy.signal.correlation_lags(len(x), len(y))
    return pd.DataFrame([lags, result], index=["lags", "ccf"]).T


def kpss_test(data: pd.DataFrame,
              incl_columns: list) -> pd.DataFrame:

    test_stat, p_val = [], []
    cv_1, cv_5, cv_10 = [], [], []
    temp_df = data[incl_columns].copy()

    for c in temp_df.columns:
        kpss_res = kpss(temp_df[c].dropna(), regression='ct')
        test_stat.append(kpss_res[0])
        p_val.append(kpss_res[1])
        cv_1.append(kpss_res[3]['1%'])
        cv_5.append(kpss_res[3]['5%'])
        cv_10.append(kpss_res[3]['10%'])
    kpss_res_df = pd.DataFrame({'Test statistic': test_stat,
                               'p-value': p_val,
                                'Critical value - 1%': cv_1,
                                'Critical value - 5%': cv_5,
                                'Critical value - 10%': cv_10},
                               index=temp_df.columns)
    kpss_res_df = kpss_res_df.round(4)

    return kpss_res_df


def adf_test(ts: pd.Series) -> pd.Series:

    dftest = adfuller(ts, autolag="AIC")
    output = pd.Series(
        dftest[0:4],
        index=[
            "Test Statistic",
            "p-value",
            "# Lags Used",
            "Number of Observations Used",
        ],
    )
    for key, value in dftest[4].items():
        output["Critical Value (%s)" % key] = value

    return output


def get_adf_df(data: pd.DataFrame,
               incl_columns: list):

    test_result = pd.DataFrame()

    for col in incl_columns:
        col_result = adf_test(data[col])
        col_result_df = pd.DataFrame(col_result)
        col_result_df.columns = [col]
        test_result = pd.concat([test_result, col_result_df.T], axis=0)

    return test_result


def cointegration_test(df, alpha=0.05):
    """
    Perform cointegration test using Johansen's test.

    Parameters:
    - df (pd.DataFrame): A DataFrame containing time series data for cointegration test.
    - alpha (float, optional): Significance level for the test. Default is 0.05.

    Returns:
    dict: A dictionary containing the results of the cointegration test.
    """
    out = coint_johansen(df, -1, 5)
    d = {'0.90': 0, '0.95': 1, '0.99': 2}
    traces = out.lr1
    cvts = out.cvt[:, d[str(1 - alpha)]]

    results = {}
    for col, trace, cvt in zip(df.columns, traces, cvts):
        results[col] = {'Test Stat': round(trace, 2), 'C(95%)': cvt, 'Significance': trace > cvt}
    return results


def grangers_causation_matrix(data, variables,
                              maxlag=15, test='ssr_chi2test', verbose=False):

    df = pd.DataFrame(np.zeros((len(variables), len(variables))),
                      columns=variables, index=variables)
    for c in df.columns:
        for r in df.index:
            test_result = grangercausalitytests(
                data[[r, c]], maxlag=maxlag, verbose=False)
            p_values = [round(test_result[i+1][0][test][1], 5)
                        for i in range(maxlag)]
            if verbose:
                print(f'Y = {r}, X = {c}, P Values = {p_values}')
            min_p_value = np.min(p_values)
            df.loc[r, c] = min_p_value
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    return df


def check_and_modify_date(date):

    if date.day != 1:
            # Modify the date to the first day of the same month
            modified_date = date.replace(day=1)
            return modified_date
    return date

def generate_search_params():
    # Set parameter range
    p, d, q = range(0, 3), range(0, 2), range(0, 3)
    P, D, Q, s = range(0, 3), range(0, 2), range(0, 3), [12]

    # list of all parameter combos
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = list(itertools.product(P, D, Q, s))
    all_param = list(itertools.product(pdq, seasonal_pdq))