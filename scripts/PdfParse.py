import os
import math
import re
import numpy as np
import pandas as pd
import pdfplumber
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
             table_num: int):

    table_loc = locate_table(filepath, search_string,
                             ignore_case=True)["table_loc"]
    if len(table_loc) != 0:
        table_num = table_loc[-1]
        dfs = tabula.read_pdf(filepath, pages=table_num, stream=True)
        df = dfs[0]
        df.columns = df.iloc[0, :].to_list()

    else:
        dfs = tabula.read_pdf(filepath, pages="all", stream=True)
        df = dfs[table_num]
        df.columns = df.iloc[0, :].to_list()

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


def remove_separator(df: pd.DataFrame):

    colnames = df.columns
    for col in colnames:
        col_series = pd.Series(df[col].values.flatten())
        df[col] = (df[col].str.replace(",", "")
                              .replace("-", "0")
                              .replace("(", "")
                              .replace(")", ""))

    return df


def separate_data(df: pd.DataFrame,
                  var: str):

    air_number, ship_number = list(), list()
    for i in df[var]:
        try:
            air, ship = i.split(" ")[0], i.split(" ")[-1]
            air_number.append(air)
            ship_number.append(ship)
        except:
            if type(i) != float:
                length = len(i.split(" "))
                if length < 2:
                    air_number.append(i.split(" ")[0])
                    ship_number.append(0)
            else:
                pass

    df["Air"], df["Ship"] = air_number, ship_number
    df = df.drop(var, axis=1)
    return df


def check_quality(df: pd.DataFrame,
                  exclude_vars: list):

    new_df = df.iloc[:, ~df.columns.isin(exclude_vars)]
    checked_vars = new_df.columns[~new_df.columns.isin(["Total"])].to_list()

    for idx in new_df.index:
        row_sum = 0
        for var in checked_vars:
            row_sum += int(new_df[var][idx])
        if int(new_df["Total"][idx]) == row_sum:
            pass
        else:
            return False
