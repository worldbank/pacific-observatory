import os
import math
import re
import numpy as np
import pandas as pd
import tabula
import PyPDF2
import warnings
warnings.filterwarnings("ignore")

## The Parser is a temporary one that could extract most stats.
## However, right now, it fails to solve the inconsistent horizontal spaces between
## Air and Ship figures in Tonga. Thus, it fails to pass the check_quality func.
## Further improvements are needed.

def locate_table(filepath: str,
                 search_string: str,
                 ignore_case=False):

    search_lst = list()
    reader = PyPDF2.PdfReader(filepath)

    for page_num, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            hits = None
            if ignore_case == False:
                hits = re.search(search_string, page_text.lower())
            else:
                hits = re.search(
                    search_string, page_text.lower(), re.IGNORECASE)

            if hits:
                search_lst.append(page_num+1)
        except:
            pass

    return {"table_loc": search_lst}


def load_pdf(filepath: str,
             search_string: str,
             table_page: int,
             table_seq = 0):

    table_loc = locate_table(filepath, search_string,
                             ignore_case=True)["table_loc"]
    if len(table_loc) != 0:
        table_page = table_loc[-1]
        dfs = tabula.read_pdf(filepath, pages=table_page, stream=True)
        if len(dfs) > 1:
            print(f"The page has {len(dfs)} tables.")
            df = dfs[table_seq]

        else:
            df = dfs[0]
            df.columns = df.iloc[0, :].to_list()
    else:
        dfs = tabula.read_pdf(filepath, pages="all", stream=True)
        df = dfs[table_page]
        df.columns = df.iloc[0, :].to_list()

    df = df.iloc[1:].reset_index().drop("index", axis=1)

    return df


def split_time(df: pd.DataFrame,
               time_var: str):

    year_idx, month_idx = list(), list()
    for idx in df.index:
        if (str(df[time_var][idx]).isdigit() == True):
            year_idx.append(idx)
        else:
            month_idx.append(idx)

    latest_year_idx = max(year_idx)

    return latest_year_idx, year_idx, month_idx


def detect_year(series: pd.Series):
    nacheck = pd.isna(series)
    start_year = int(series[nacheck == False][0])
    return start_year


def generate_time(df: pd.DataFrame,
                  start_year: int):

    years = [start_year + idx // 12 for idx in df.index]
    df["Year"] = years

    return df


def remove_separator(df: pd.DataFrame):

    colnames = df.columns
    for col in colnames:
        try:
            if df[col].dtype == "O":
                df[col] = (df[col].str.replace(",", "")
                                  .str.replace("-", "")
                                  .str.replace("(", "")
                                  .str.replace(")", "")
                                  .str.replace(" ", ""))
        except:
            print(col, "might have an error.")

    return df



def separate_data(df: pd.DataFrame,
                  var: str,
                  split_rule: str):

    splited_lst = var.split(split_rule)
    var_number = len(splited_lst)

    obj = dict()
    for i in range(var_number):
        obj[str(splited_lst[i])] = []

    for i in df[var]:
        elems = i.split(" ")
        length = len(elems)
        if length == var_number:
            idx, var = 0, list(obj.keys())
            while idx < length:
                key, val = var[idx], elems[idx]
                obj[key].append(val)
                idx += 1

        elif length < var_number:
            idx, var = 0, list(obj.keys())
            while idx < length and len(elems) != 0:
                key, val = var[idx], elems[idx].split(" ")[0]
                obj[key].append(val)
                elems = i.replace(val, "").strip()
                idx += 1
            else:
                key, val = var[idx], 0
                obj[key].append(val)
                idx += 1

        else:
            idx, var = 0, list(obj.keys())
            while idx < var_number:
                key, val = var[idx], elems[idx]
                obj[key].append(val)
                idx += 1
            else:
                key, val = var[-1], elems[idx]
                prev_val = obj[key][-1]
                obj[key][-1] = prev_val + val

    for i in range(var_number):
        df[str(splited_lst[i])] = obj[list(obj.keys())[i]]

    return df


def check_quality(df: pd.DataFrame,
                  exclude_vars: list,
                  sum_var: str):

    new_df = df.iloc[:, ~df.columns.isin(exclude_vars)]
    checked_vars = new_df.columns[~new_df.columns.isin([sum_var])].to_list()
    error_lst = []

    for idx in new_df.index:
        row_sum = 0
        for var in checked_vars:
            val = new_df[var][idx]
            if math.isnan(float(val)) != True:
                row_sum += float(val)
            else:
                row_sum += 0
        if float(new_df[sum_var][idx]) == (row_sum):
            pass
        else:
            error_lst.append(idx)
            # return False Previous version
    return error_lst
