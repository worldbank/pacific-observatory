import pandas as pd
import numpy as np


def cross_corr_df(data: pd.DataFrame,
                  series_a: str,
                  series_b: str) -> pd.DataFrame:

    from statsmodels.tsa.stattools import ccf

    sig_a, sig_b = data[series_a], data[series_b]

    ccorr = ccf(sig_a, sig_b, adjusted=False)

    ccorr_df = (pd.DataFrame(ccorr)
                .reset_index()
                .rename({"index": "lag", 0: "cross_corr_coef"}, axis=1))

    return ccorr_df


def kpss_test(data: pd.DataFrame,
              incl_columns: list) -> pd.DataFrame:

    from statsmodels.tsa.stattools import kpss
    import warnings
    warnings.filterwarnings("ignore")

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

    from statsmodels.tsa.stattools import adfuller

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



def grangers_causation_matrix(data, variables,
                              maxlag=15, test='ssr_chi2test', verbose=False):

    from statsmodels.tsa.stattools import grangercausalitytests

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

def scaledlogit_transform(series):
    upper, lower = series.max() + 1, series.min() - 1
    scaled_logit = np.log((series - lower)/(upper - series))

    return scaled_logit

def inverse_scaledlogit(trans_series, upper, lower):
    exp = np.exp(trans_series)
    inv_series = (((upper - lower) * exp) / (1 + exp)) + lower
    return inv_series


def check_and_modify_date(date):

    if date.day != 1:
            # Modify the date to the first day of the same month
            modified_date = date.replace(day=1)
            return modified_date
    return date
