import os
import pandas as pd
import numpy as np
from .utils import (
    is_in_word_list
)

ECON_LIST = [
    "economy", "economic", "economics", "business", "commerce", "finance",
    "industry"
]

POLICY_LIST = [
    "government", "governmental", "authorities", "minister", "ministry",
    "parliament", "parliamentary", "tax", "regulation", "legislation",
    "central bank", "cbsi", "imf", "world bank", "international monetary fund",
    "debt"
]

UNCERTAINTY_LIST = [
    "uncertain", "uncertainty", "uncertainties", "unknown", "unstable",
    "unsure", "undetermined", "risky", "risk", "not certain", "non-reliable"
]


class EPU:
    def __init__(self, filepath, econ_terms=ECON_LIST, policy_terms=POLICY_LIST, uncertainty_terms=UNCERTAINTY_LIST, **kwargs):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Cannot find {filepath}")
        self.filepath = filepath
        self.econ_terms = econ_terms
        self.policy_terms = policy_terms
        self.uncertainty_terms = uncertainty_terms

    @staticmethod
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

    @staticmethod
    def get_count(data: pd.DataFrame, column: str) -> pd.DataFrame:
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

    def get_epu_category(self):
        self.raw = self.process_data(self.filepath)
        for col, terms in zip(["econ", "policy", "uncertain"], [self.econ_terms, self.policy_terms, self.uncertainty_terms]):
            self.raw[col] = self.raw["news"].str.lower().apply(
                is_in_word_list, terms=terms)
        self.raw["epu"] = (self.raw.econ == True) & (
            self.raw.policy == True) & (self.raw.uncertain == True)

    def get_epu_stats(self, cutoff: str = None) -> pd.DataFrame:
        news_count = self.get_count(self.raw, "news")
        epu_count = self.get_count(self.raw[self.raw["epu"] == True], "epu")
        self.epu_stat = news_count.merge(
            epu_count, how="left", on="ym").fillna(0)
        self.epu_stat["date"] = pd.to_datetime(self.epu_stat["ym"])

        # Check for date integrity
        self.min_date, self.max_date = self.epu_stat.date.min(), self.epu_stat.date.max()
        self.date_df = pd.DataFrame(pd.date_range(
            self.min_date, self.max_date, freq="MS"), columns=["date"])

        self.epu_stat = (self.date_df.merge(self.epu_stat, how="left", on="date")
                         .fillna(0).drop("ym", axis=1))
        self.epu_stat["ratio"] = self.epu_stat["epu_count"] / \
            self.epu_stat["news_count"]

        if cutoff != None:
            std = self.epu_stat[self.epu_stat.date <= cutoff]["ratio"].std()

        std = self.epu_stat["ratio"].std()
        self.epu_stat["z_score"] = self.epu_stat['ratio']/std

        return self.epu_stat
