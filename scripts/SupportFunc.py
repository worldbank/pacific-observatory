import os
import urllib3
import datetime
import pandas as pd
import numpy as np

# Wrap the urllib3 downloading functions
def download_files(url:str, path:str, chunk_size=1024):
    """
    Args
    ------
    url: string
        The string of URL for downloading.
    path: string
        The string of the saving path.
    chuck_sise: int
        The default is set as 1024.

    Return
    ------
        N/A
    """

    http = urllib3.PoolManager()
    r = http.request(
        'GET',
        url,
        preload_content=False)

    with open(path, 'wb') as out:
        while True:
            data = r.read(chunk_size)
            if not data:
                break
            out.write(data)
    r.release_conn()


def create_month_mapping():

    month_equv = dict()

    for i in range(1, 13):
        month_abbre = datetime.date(1900, i, 1).strftime('%b')
        month_full = datetime.date(1900, i, 1).strftime('%B')
        month_equv.update({month_full: i, month_abbre: i})

    return month_equv


def parse_filename(filename: str) -> dict:

    filename_lst = filename.replace(".csv", "").split("-")

    identifier = {"year": [], "month": []}
    for elem in filename_lst:
        if elem.isdigit() == True:
            if len(elem) == 4:
                identifier["year"].append(elem)
        else:
            temp_dict = create_month_mapping()
            for (key, val) in temp_dict.items():
                if elem in key:
                    identifier["month"].append(val)

    return identifier


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
