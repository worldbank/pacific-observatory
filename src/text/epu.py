import os
import pandas as pd
import numpy as np
from .utils import (
    is_in_word_list
)


def process_data(filepath: str) -> pd.DataFrame:
    """
    Reads a CSV file and processes the data.

    Args:
        filename (str): The name of the CSV file.
        folderpath (str): The path to the folder containing the CSV file.

    Returns:
        pd.DataFrame: Processed DataFrame with the "Unnamed: 0" column dropped,
                      newline characters removed from the "news" column,
                      "date" column converted to datetime, and a new "ym" column added.
    """
    df = pd.read_csv(filepath).drop("Unnamed: 0", axis=1)
    df["news"] = df["news"].replace("\n", "")
    df["date"] = pd.to_datetime(df["date"])
    df["ym"] = [str(d.year) + "-" + str(d.month) for d in df.date]
    return df


def get_news_count(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Computes the count of occurrences for a specific column in a DataFrame
    grouped by the year-month ('ym').

    Args:
        data (pd.DataFrame): The input DataFrame.
        column (str): The column for which the count is computed.

    Returns:
        pd.DataFrame: DataFrame with the count of occurrences for the specified column
           
    """
    count_df = (data.set_index("date")
                    .groupby("ym")[[str(column)]]
                    .count()
                    .reset_index()
                    .rename({str(column): str(column) + "_count"}, axis=1))
    return count_df
